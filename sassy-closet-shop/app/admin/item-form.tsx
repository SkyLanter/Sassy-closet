"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { linkPipelineIntakeAction, setPipelineStageAction, uploadImageAction } from "@/app/admin/actions";
import { EditorCard, EditorSectionNav } from "@/app/admin/editor-chrome";
import { Area, Field, FormAlert } from "@/app/admin/fields";
import { applyColorsToDraft, ImageFields } from "@/app/admin/image-fields";
import { PriceCalculator } from "@/app/admin/price-calculator";
import { AdminColorEditor } from "@/components/admin-colors";
import { AdminSizeEditor } from "@/components/admin-sizes";
import { MaMark } from "@/components/ma-mark";
import { emptyFitCm } from "@/lib/asia-size";
import { messageReadyAddFields } from "@/lib/admin-add";
import { postAdminAdd, postAdminRemove, postAdminRename, postAdminSave, recoverAddedMa } from "@/lib/admin-client-save";
import { letterPickerOptions, TYPE_LABELS } from "@/lib/catalog";
import { isKnownSeedMa } from "@/lib/catalog-contract";
import { nextImageOrder } from "@/lib/hub-colors";
import { prefillToDraft, type IntakePrefill } from "@/lib/intake-import";
import { consumeIntakePrefill } from "@/lib/intake-prefill";
import type { ItemDraft } from "@/lib/item-draft";
import { parseDraftPrice, validateItemDraft } from "@/lib/item-draft";
import { isValidMa, MA_LETTERS, nextMaForLetter, normalizeMa, type MaLetter } from "@/lib/ma";
import { isOpaqueRscError, opaquePostSaveMessage, publicSaveErrorMessage } from "@/lib/opaque-rsc-error";
import { statusLabel } from "@/lib/site-settings";
import type { CatalogStorageInfo } from "@/lib/storage-info";
import { saveConfirmLine, saveConfirmPrompt } from "@/lib/save-confirm";
import { isCompleteSaveReceipt, saveReceiptLine, silentSaveError } from "@/lib/save-receipt";
import type { Product, ProductImageAsset, SiteSettings } from "@/lib/types";
import {
  uploadOverServerActionLimit,
  uploadTooLargeError,
} from "@/lib/upload-limits";

export function draftFromProduct(product: Product): ItemDraft {
  return {
    titleEn: product.titleEn,
    titleVn: product.titleVn,
    descriptionEn: product.descriptionEn,
    descriptionVn: product.descriptionVn,
    status: product.status,
    priceInput: product.priceUsd === null ? "" : String(product.priceUsd),
    colors: product.colors,
    images: product.images.length > 0 ? product.images : [{ src: "", colorId: null, order: 1 }],
    sizes: product.sizes,
    fitCm: product.fitCm,
    fulfillment: product.fulfillment,
    sourceLink: product.sourceLink ?? "",
  };
}

export function emptyDraft(letter: MaLetter = "A"): ItemDraft {
  const starter = messageReadyAddFields(letter);
  return {
    titleEn: starter.titleEn,
    titleVn: starter.titleVn,
    descriptionEn: starter.descriptionEn,
    descriptionVn: starter.descriptionVn,
    status: "hold",
    priceInput: "",
    colors: starter.colors,
    images: [{ src: "", colorId: null, order: 1 }],
    sizes: starter.sizes ?? [],
    fitCm: starter.fitCm ?? emptyFitCm(),
    fulfillment: "dropship",
    sourceLink: "",
  };
}

type ToastFn = (tone: "ok" | "error", text: string) => void;

function snapshotDraft(draft: ItemDraft, renameInput: string): string {
  return JSON.stringify({ draft, renameInput });
}

export function ItemForm({
  mode,
  product,
  products,
  storage,
  notice,
  onToast,
  onCatalog,
  onCancel,
}: {
  mode: "add" | "edit";
  product?: Product;
  products: Product[];
  storage: CatalogStorageInfo;
  notice?: string;
  onToast: ToastFn;
  onCatalog: (
    products: Product[],
    settings: SiteSettings,
    options?: { nextMa?: string; renamedTo?: string; removed?: boolean },
  ) => void;
  onCancel: () => void;
}) {
  const [saving, setSaving] = useState(false);
  // Intake prefill: consumed once from sessionStorage (written by the Intake
  // import page). Null on edit mode and on direct visits to /admin/new.
  const [prefill] = useState<IntakePrefill | null>(() =>
    mode === "add" && !product ? consumeIntakePrefill() : null,
  );
  const [addLetter, setAddLetter] = useState<MaLetter>(() => {
    if (product?.type) {
      return product.type;
    }
    const letter = prefill?.letter?.toUpperCase() ?? "";
    return (MA_LETTERS as readonly string[]).includes(letter) ? (letter as MaLetter) : "A";
  });
  const [draft, setDraft] = useState<ItemDraft>(() =>
    product ? draftFromProduct(product) : prefill ? prefillToDraft(prefill) : emptyDraft("A"),
  );
  const [renameInput, setRenameInput] = useState(product?.ma ?? "");
  const [formError, setFormError] = useState<string | null>(null);
  const [formOk, setFormOk] = useState<string | null>(notice ?? null);
  const bannerRef = useRef<HTMLDivElement>(null);
  const baselineRef = useRef(
    snapshotDraft(product ? draftFromProduct(product) : emptyDraft(), product?.ma ?? ""),
  );
  const dirty = snapshotDraft(draft, renameInput) !== baselineRef.current;

  useEffect(() => {
    if (typeof window === "undefined" || window.location.hash !== "#ma") {
      return;
    }
    document.getElementById("ma")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  useEffect(() => {
    if (!dirty) {
      return;
    }
    function onLeave(event: BeforeUnloadEvent) {
      event.preventDefault();
      event.returnValue = "";
    }
    window.addEventListener("beforeunload", onLeave);
    return () => window.removeEventListener("beforeunload", onLeave);
  }, [dirty]);

  function confirmLeave(): boolean {
    if (!dirty) {
      return true;
    }
    return window.confirm("Leave without saving? The shop will not see these edits.");
  }

  const predictedMa = useMemo(
    () => nextMaForLetter(addLetter, products.map((item) => item.ma)),
    [addLetter, products],
  );

  const currentMa = mode === "edit" && product ? product.ma : predictedMa;
  const uploading = draft.images.some((image) => image.src.startsWith("blob:"));
  const busy = saving;
  const draftPriceUsd = parseDraftPrice(draft.status, draft.priceInput);
  const confirmLine = saveConfirmLine(
    currentMa,
    draft.status,
    Number.isNaN(draftPriceUsd) ? null : draftPriceUsd,
  );

  function showError(text: string) {
    const display = isOpaqueRscError(text) ? opaquePostSaveMessage() : text;
    setFormOk(null);
    setFormError(display);
    onToast("error", display);
    window.requestAnimationFrame(() => {
      bannerRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  function showOk(text: string) {
    setFormError(null);
    setFormOk(text);
    onToast("ok", text);
  }

  function finishAdd(savedMa: string, message: string) {
    baselineRef.current = snapshotDraft(draft, savedMa);
    showOk(message);
    markPipelineSaved(savedMa);
    if (prefill && prefill.intakeMa !== savedMa) {
      void linkPipelineIntakeAction(savedMa, prefill.intakeMa).then((result) => {
        if (!result.ok) {
          onToast("error", `Saved, but the pipeline tracker did not link intake ${prefill.intakeMa}: ${result.error}`);
        }
      });
    }
    onCatalog(products, { announcementLines: [], facebookPageUrl: "" }, { nextMa: savedMa });
  }

  /** Auto-advance the pipeline tracker: a catalog save means the sell tab is staged. */
  function markPipelineSaved(ma: string) {
    if (!storage.canWrite) {
      return;
    }
    void setPipelineStageAction(ma, "sell_tab", true).then((result) => {
      if (!result.ok) {
        onToast("error", `Saved, but the pipeline tracker did not update: ${result.error}`);
      }
    });
  }

  function payload() {
    const priceUsd = parseDraftPrice(draft.status, draft.priceInput);
    return {
      titleEn: draft.titleEn,
      titleVn: draft.titleVn,
      descriptionEn: draft.descriptionEn,
      descriptionVn: draft.descriptionVn,
      status: draft.status,
      priceUsd: Number.isNaN(priceUsd) ? null : priceUsd,
      colors: draft.colors,
      images: draft.images,
      sizes: draft.sizes,
      fitCm: draft.fitCm,
      fulfillment: draft.fulfillment,
      sourceLink: draft.sourceLink.trim() ? draft.sourceLink.trim() : null,
    };
  }

  async function submit() {
    const previousMas = products.map((item) => item.ma);
    try {
      const error = validateItemDraft(draft);
      if (error) {
        showError(error);
        return;
      }
      if (!storage.canWrite) {
        showError("Cannot save: storage is not configured. Set BLOB_READ_WRITE_TOKEN on Vercel.");
        return;
      }
      setSaving(true);
      if (mode === "add") {
        const result = await postAdminAdd({ letter: addLetter, ...payload() });
        if (!result.ok) {
          const recovered = await recoverAddedMa(previousMas, addLetter);
          if (recovered) {
            finishAdd(recovered, `Saved ${recovered} · Blob wrote; opening the item.`);
            return;
          }
          showError(result.error);
          return;
        }
        if (!isCompleteSaveReceipt(result)) {
          const recovered = await recoverAddedMa(previousMas, addLetter);
          if (recovered) {
            finishAdd(recovered, `Saved ${recovered} · Blob wrote; opening the item.`);
            return;
          }
          showError(silentSaveError());
          return;
        }
        const savedMa = result.nextMa || result.ma || predictedMa;
        finishAdd(savedMa, `Saved ${savedMa} · ${saveReceiptLine(result)}.`);
        return;
      }
      const result = await postAdminSave({ ma: currentMa, ...payload() });
      if (!result.ok) {
        showError(result.error);
        return;
      }
      if (!isCompleteSaveReceipt(result)) {
        showError(silentSaveError());
        return;
      }
      baselineRef.current = snapshotDraft(draft, renameInput);
      if (result.products && result.settings) {
        onCatalog(result.products, result.settings);
      }
      showOk(`Saved ${result.ma || currentMa} · ${saveReceiptLine(result)}.`);
      markPipelineSaved(result.ma || currentMa);
    } catch (error) {
      if (mode === "add") {
        const recovered = await recoverAddedMa(previousMas, addLetter);
        if (recovered) {
          finishAdd(recovered, `Saved ${recovered} · Blob wrote; opening the item.`);
          return;
        }
      }
      showError(publicSaveErrorMessage(error, opaquePostSaveMessage()));
    } finally {
      setSaving(false);
    }
  }

  async function changeMa() {
    if (mode !== "edit" || !product) {
      return;
    }
    const to = normalizeMa(renameInput);
    if (!isValidMa(to)) {
      showError(
        "New mã must be one allowed letter plus digits (example A04). Letters: A Q V K G B P H J S O D. Official AO001 is refused.",
      );
      return;
    }
    if (to !== product.ma && products.some((item) => normalizeMa(item.ma) === to)) {
      showError(`Mã ${to} already exists. Do not gộp. Pick an unused mã.`);
      return;
    }
    if (isKnownSeedMa(product.ma) && to !== product.ma) {
      showError(`Cannot rename hub mã ${product.ma}. Keep the ten. Add a new piece instead.`);
      return;
    }
    const error = validateItemDraft(draft);
    if (error) {
      showError(error);
      return;
    }
    if (!storage.canWrite) {
      showError("Cannot change mã: storage is not configured.");
      return;
    }
    if (!window.confirm(saveConfirmPrompt(`Change mã ${product.ma} → ${to} · ${confirmLine}`))) {
      return;
    }
    setSaving(true);
    try {
      const result = await postAdminRename({ from: product.ma, to, ...payload() });
      if (!result.ok) {
        showError(result.error);
        return;
      }
      if (!isCompleteSaveReceipt(result) || !result.products || !result.settings) {
        showError(silentSaveError());
        return;
      }
      baselineRef.current = snapshotDraft(draft, to);
      onCatalog(result.products, result.settings, { renamedTo: result.renamedTo });
      showOk(`Changed mã ${product.ma} → ${result.renamedTo} · ${saveReceiptLine(result)}.`);
    } catch (error) {
      showError(publicSaveErrorMessage(error, opaquePostSaveMessage()));
    } finally {
      setSaving(false);
    }
  }

  async function removeItem() {
    if (mode !== "edit" || !product) {
      return;
    }
    if (!storage.canWrite) {
      showError("Cannot remove: storage is not configured.");
      return;
    }
    const confirmed = window.confirm(
      `Remove ${product.ma} from the live catalog? It will leave the shop. This does not invent a new mã.`,
    );
    if (!confirmed) {
      return;
    }
    setSaving(true);
    try {
      const result = await postAdminRemove(product.ma);
      if (!result.ok) {
        showError(result.error);
        return;
      }
      if (!isCompleteSaveReceipt(result) || !result.products || !result.settings) {
        showError(silentSaveError());
        return;
      }
      onToast("ok", `Removed ${product.ma} · ${saveReceiptLine(result)}.`);
      onCatalog(result.products, result.settings, { removed: true });
    } catch (error) {
      showError(publicSaveErrorMessage(error, opaquePostSaveMessage()));
    } finally {
      setSaving(false);
    }
  }

  async function onUpload(file: File, colorId: string | null) {
    if (uploadOverServerActionLimit(file.size)) {
      showError(uploadTooLargeError(file.size));
      return;
    }
    const localUrl = URL.createObjectURL(file);
    const incoming: ProductImageAsset = {
      src: localUrl,
      colorId,
      order: nextImageOrder(draft.images.filter((image) => image.src.trim())),
    };
    setDraft((current) => ({
      ...current,
      images: [...current.images.filter((image) => image.src.trim()), incoming],
    }));
    const form = new FormData();
    form.set("file", file);
    let result: Awaited<ReturnType<typeof uploadImageAction>>;
    try {
      result = await uploadImageAction(currentMa, form);
    } catch (error) {
      URL.revokeObjectURL(localUrl);
      setDraft((current) => ({
        ...current,
        images: current.images.filter((image) => image.src !== localUrl),
      }));
      showError(error instanceof Error ? error.message : "Upload failed. Photo was not saved.");
      return;
    }
    if (!result.ok) {
      URL.revokeObjectURL(localUrl);
      setDraft((current) => ({
        ...current,
        images: current.images.filter((image) => image.src !== localUrl),
      }));
      showError(result.error);
      return;
    }
    setDraft((current) => ({
      ...current,
      images: current.images.map((image) =>
        image.src === localUrl ? { ...image, src: result.url } : image,
      ),
    }));
    URL.revokeObjectURL(localUrl);
  }

  const sectionNav =
    mode === "add"
      ? [
          { id: "identity", label: "Identity" },
          { id: "status", label: "Status & price" },
          { id: "fit", label: "Size & fit" },
          { id: "media", label: "Colors & photos" },
          { id: "copy", label: "Copy" },
        ]
      : [
          { id: "identity", label: "Identity" },
          { id: "ma", label: "Change mã" },
          { id: "status", label: "Status & price" },
          { id: "fit", label: "Size & fit" },
          { id: "media", label: "Colors & photos" },
          { id: "copy", label: "Copy" },
        ];

  return (
    <div className="space-y-6 pb-28">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-[11px] uppercase tracking-[0.18em] text-muted">
            {mode === "add" ? "New item" : "Edit item"}
          </p>
          <h2 className="mt-1 font-display text-4xl text-ink">
            {mode === "add" ? (
              "Add mã"
            ) : (
              <MaMark ma={currentMa} className="text-4xl tracking-[0.06em]" />
            )}
          </h2>
          <p className="mt-2 text-sm text-muted">
            {mode === "add"
              ? "Assigned on Save — not a shop tile until receipt. Blob write + revalidate, never a silent fail."
              : `${TYPE_LABELS[product?.type ?? "A"].nav} · ${statusLabel(draft.status)}`}
          </p>
          {mode === "add" ? (
            <p className="mt-3 max-w-xl text-sm text-gold-deep">
              Sell-test is polish-only. Do not Add a new mã until Boss reopens the catalog.
            </p>
          ) : null}
          {mode === "add" && prefill ? (
            <p
              className="mt-3 max-w-xl rounded-xl border border-line bg-blush/60 px-4 py-3 text-sm text-ink"
              data-testid="admin-intake-prefill"
            >
              Prefilled from intake <MaMark ma={prefill.intakeMa} className="text-[1em] tracking-[0.1em]" /> —
              staged only (hold, never available, never Square).
              {prefill.suggestedSell !== null ? ` Suggested sell $${prefill.suggestedSell}.` : ""}{" "}
              Titles and swatch hexes still need you before Save.
            </p>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2">
          {mode === "edit" && draft.status !== "sold" ? (
            <Link
              href={`/m/${currentMa}`}
              target="_blank"
              className="rounded-full border border-line px-4 py-2 text-xs uppercase tracking-[0.12em] text-ink hover:border-gold"
            >
              Preview PDP
            </Link>
          ) : null}
          <button
            type="button"
            onClick={() => {
              if (confirmLeave()) {
                onCancel();
              }
            }}
            className="rounded-full border border-line px-4 py-2 text-xs uppercase tracking-[0.12em] text-muted hover:text-ink"
          >
            Back to catalog
          </button>
        </div>
      </div>

      <EditorSectionNav items={sectionNav} />

      <div ref={bannerRef} className="space-y-2">
        {formError ? <FormAlert tone="error" text={formError} /> : null}
        {formOk ? <FormAlert tone="ok" text={formOk} /> : null}
        {uploading ? (
          <FormAlert tone="error" text="Image still uploading. Wait for it to finish, then Add/Save." />
        ) : null}
      </div>

      <EditorCard
        id="identity"
        eyebrow="1"
        title="Identity"
        hint={
          mode === "add"
            ? "Pick a letter only (A · Tops). The next unused code is assigned on Save — unused letters are not shop tiles. English title is required."
            : "Titles customers see. Type follows the mã letter. Same mã — this is edit, not rename."
        }
      >
        {mode === "add" ? (
          <div className="space-y-2" data-next-ma-trap="off" data-testid="admin-add-form">
            <label className="block text-xs uppercase tracking-[0.14em] text-muted">
              Letter
              <select
                data-testid="admin-add-letter"
                className="mt-1 w-full max-w-xs rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
                value={addLetter}
                onChange={(event) => {
                  const letter = letterPickerOptions().find((option) => option.letter === event.target.value);
                  if (letter) {
                    setAddLetter(letter.letter);
                    setDraft((current) => {
                      const starter = messageReadyAddFields(letter.letter);
                      return {
                        ...current,
                        titleEn: starter.titleEn,
                        titleVn: starter.titleVn,
                        descriptionEn: starter.descriptionEn,
                        descriptionVn: starter.descriptionVn,
                        status: "hold",
                        priceInput: "",
                      };
                    });
                  }
                }}
              >
                {letterPickerOptions().map((option) => (
                  <option key={option.letter} value={option.letter}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <p className="text-sm text-muted" data-testid="admin-assigned-on-save">
              Assigned on Save — not a shop tile until the Blob receipt. Prediction:{" "}
              <MaMark ma={predictedMa} className="text-[13px] tracking-[0.12em]" />
            </p>
          </div>
        ) : null}
        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="Title (EN)"
            testId="admin-title-en"
            value={draft.titleEn}
            required
            placeholder="e.g. White knit set with belt"
            hint="Shown on the shop tile. Required — Save refuses a blank English title."
            onChange={(titleEn) => setDraft((current) => ({ ...current, titleEn }))}
          />
          <Field
            label="Title (VN flavor)"
            value={draft.titleVn}
            placeholder="e.g. Set len trắng kèm thắt lưng"
            hint="Optional Vietnamese flavor under the English title."
            onChange={(titleVn) => setDraft((current) => ({ ...current, titleVn }))}
          />
        </div>
      </EditorCard>

      {mode === "edit" && product ? (
        <EditorCard
          id="ma"
          eyebrow="2"
          title="Change mã"
          hint="Official crawl #27: rename must be visible and unique. Hub ten stay. Extras move to an unused valid mã (not A01, not AO001). Photo URLs stay so thumbs do not 404. Old /m/{from} leaves the shop."
        >
          {isKnownSeedMa(product.ma) ? (
            <p className="text-sm text-gold-deep">
              {product.ma} is a hub mã. Keep the ten. Add a new piece instead of renaming this row.
            </p>
          ) : (
            <p className="text-sm text-muted">
              Next unused for this letter is {nextMaForLetter(product.type, products.map((item) => item.ma))}.
              Taken mãs are refused — do not gộp.
            </p>
          )}
          <div className="mt-3 flex max-w-md flex-wrap items-end gap-3">
            <div className="min-w-[10rem] flex-1">
              <Field
                label="New mã"
                testId="admin-rename-input"
                value={renameInput}
                onChange={setRenameInput}
                placeholder={nextMaForLetter(product.type, products.map((item) => item.ma))}
                disabled={isKnownSeedMa(product.ma)}
              />
            </div>
            <button
              type="button"
              data-testid="admin-rename-ma"
              disabled={saving || uploading || isKnownSeedMa(product.ma)}
              onClick={changeMa}
              className="rounded-full bg-ink px-4 py-2 text-sm text-paper disabled:opacity-40"
            >
              Save & change mã
            </button>
            <button
              type="button"
              data-testid="admin-remove-item"
              disabled={saving || uploading}
              onClick={removeItem}
              className="rounded-full border border-line px-4 py-2 text-sm text-muted hover:text-ink disabled:opacity-40"
            >
              Remove from catalog
            </button>
          </div>
        </EditorCard>
      ) : null}

      <EditorCard
        id="status"
        eyebrow="3"
        title="Status & price"
        hint="Sell-facing tiles are hold | available. Hold = Nhắn tin hỏi giá (no USD). Sold / Gone hides the tile and retires the mã. Qty is 1 (unique piece), not a warehouse count. Dropship is the default."
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block text-xs uppercase tracking-[0.14em] text-muted">
            Status
            <select
              className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
              value={draft.status}
              onChange={(event) => {
                const status = event.target.value;
                if (status !== "available" && status !== "hold" && status !== "sold") {
                  return;
                }
                setDraft((current) => ({
                  ...current,
                  status,
                  priceInput: status === "hold" ? "" : current.priceInput,
                }));
              }}
            >
              <option value="hold">Hold · Inbox for price</option>
              <option value="available">Available</option>
              <option value="sold">Sold / Gone (hidden from shop)</option>
            </select>
          </label>
          <Field
            label="Price USD"
            value={draft.status === "hold" ? "" : draft.priceInput}
            disabled={draft.status === "hold"}
            placeholder={draft.status === "hold" ? "Inbox for price" : "25"}
            hint={
              draft.status === "sold"
                ? "Optional last price. Sold items do not appear on the shop."
                : draft.status === "hold"
                  ? "Hold shows “Inbox for price” on the shop — no USD until the calculator below says the margin is safe."
                  : "Run the calculator below first — sell = ceil(landed ÷ 0.7). Whole dollars are fine."
            }
            onChange={(priceInput) => setDraft((current) => ({ ...current, priceInput }))}
          />
          <label className="block text-xs uppercase tracking-[0.14em] text-muted">
            Fulfillment
            <select
              className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
              value={draft.fulfillment}
              onChange={(event) => {
                const fulfillment = event.target.value;
                if (fulfillment !== "dropship" && fulfillment !== "on_hand") {
                  return;
                }
                setDraft((current) => ({ ...current, fulfillment }));
              }}
            >
              <option value="dropship">Dropship · source from Taobao after message</option>
              <option value="on_hand">On hand · Boss received (not Square)</option>
            </select>
          </label>
          <Field
            label="Taobao source link"
            value={draft.sourceLink}
            onChange={(sourceLink) => setDraft((current) => ({ ...current, sourceLink }))}
            placeholder="https://e.tb.cn/… (only if you have it)"
            hint="Paste a real e.tb.cn / taobao.com link. Leave blank if you do not have one. Never invent."
          />
        </div>
        <div className="mt-4">
          <PriceCalculator
            letter={product?.type ?? addLetter}
            initialCostCny={prefill?.costCny ?? null}
            initialCostUsd={prefill?.costUsd ?? null}
            initialSell={prefill?.suggestedSell ?? null}
            onApplySell={(sell) => {
              setDraft((current) => ({ ...current, priceInput: String(sell) }));
              if (mode === "edit" && product) {
                void setPipelineStageAction(product.ma, "priced", true).then((result) => {
                  if (!result.ok) {
                    onToast("error", result.error);
                  }
                });
              }
            }}
            idPrefix={`item-${mode}`}
          />
        </div>
      </EditorCard>

      <EditorCard
        id="fit"
        eyebrow="4"
        title="Size & fit"
        hint="Asia letters + stored cm only. Empty is honest. Never invent a mã, a US size, or cm from a letter."
      >
        <AdminSizeEditor
          sizes={draft.sizes}
          fitCm={draft.fitCm}
          onSizesChange={(sizes) => setDraft((current) => ({ ...current, sizes }))}
          onFitChange={(fitCm) => setDraft((current) => ({ ...current, fitCm }))}
        />
      </EditorCard>

      <EditorCard
        id="media"
        eyebrow="5"
        title="Colors & photos"
        hint="Tag photos to a color already on this mã, or leave colorId null. Hub slugs only on the ten — never invent a colorway or a mã. Pretty gallery does not release Hold."
      >
        {draft.status === "hold" || currentMa === "P02" || currentMa === "P05" ? (
          <p
            className="rounded-2xl border border-gold-deep/40 bg-blush px-4 py-3 text-sm text-gold-deep"
            data-testid="admin-hold-media"
          >
            {currentMa} is Hold · Inbox for price. A pretty gallery does not publish a USD price —
            it stays message-first (dropship after inbox).
          </p>
        ) : null}
        <AdminColorEditor
          ma={currentMa}
          colors={draft.colors}
          images={draft.images}
          canUpload={storage.canUpload}
          onNotice={(tone, text) => {
            if (tone === "error") {
              showError(text);
              return;
            }
            onToast(tone, text);
          }}
          onColorsChange={(colors) => setDraft((current) => applyColorsToDraft(current, colors))}
          onImagesChange={(images) => setDraft((current) => ({ ...current, images }))}
          onUpload={(file, colorId) => onUpload(file, colorId)}
        />
        <ImageFields
          ma={currentMa}
          draft={draft}
          canUpload={storage.canUpload}
          onChange={setDraft}
          onUpload={(file) => onUpload(file, null)}
        />
      </EditorCard>

      <EditorCard
        id="copy"
        eyebrow="6"
        title="Copy"
        hint="English is the product page default. Vietnamese flavor sits under it. Dropship: never write on hand / đang có. Message-first — no invented ship $ or day-count ETAs."
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <Area
            label="Description (EN)"
            value={draft.descriptionEn}
            placeholder="Fabric, fit, and care in a line or two. Never write “on hand” for dropship."
            onChange={(descriptionEn) => setDraft((current) => ({ ...current, descriptionEn }))}
          />
          <Area
            label="Description (VN flavor)"
            value={draft.descriptionVn}
            placeholder="Chất vải, form dáng… giọng shop cute."
            onChange={(descriptionVn) => setDraft((current) => ({ ...current, descriptionVn }))}
          />
        </div>
      </EditorCard>

      <div
        className="ky-chrome-blur fixed inset-x-0 bottom-0 z-40 border-t border-line bg-paper/95 px-4 py-3 backdrop-blur-md"
        style={{ paddingBottom: "max(0.75rem, env(safe-area-inset-bottom))" }}
      >
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-3">
          <p className="w-full text-xs text-muted sm:w-auto" data-testid="admin-save-confirm">
            {confirmLine}
          </p>
          <button
            type="button"
            data-testid="admin-save-item"
            data-save-intent="write"
            onClick={() => {
              void submit();
            }}
            disabled={busy || uploading}
            aria-busy={busy}
            className="min-h-11 shrink-0 touch-manipulation rounded-full bg-ink px-6 py-2.5 text-sm text-paper disabled:opacity-40"
          >
          {busy ? "Saving…" : null}
            {!busy && uploading ? "Wait for upload…" : null}
            {!busy && !uploading && mode === "add" ? (
              <>Save new mã{dirty ? " · unsaved" : ""}</>
            ) : null}
            {!busy && !uploading && mode === "edit" ? (
              <>
                Save <MaMark ma={currentMa} className="text-[1em] tracking-[0.1em]" />
                {dirty ? " · unsaved" : ""}
              </>
            ) : null}
          </button>
          {!storage.canWrite ? (
            <p className="text-sm text-gold-deep">Saves are blocked until Blob or KV is set on Vercel.</p>
          ) : null}
          <div aria-live="assertive" className="min-w-0 flex-1">
            {formError ? (
              <p className="text-sm text-gold-deep" data-testid="admin-save-error">
                {formError}
              </p>
            ) : null}
            {formOk && !formError ? (
              <p className="text-sm text-ink" data-testid="admin-save-receipt">
                {formOk}
              </p>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
