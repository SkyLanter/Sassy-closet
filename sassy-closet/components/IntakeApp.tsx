"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ConfirmDialog, ToastStack, type ToastItem } from "@/components/AdminChrome";
import { AskPanel } from "@/components/AskPanel";
import { BrandHeader } from "@/components/BrandHeader";
import { FindMaCard } from "@/components/FindMaCard";
import { PhotoLightbox } from "@/components/PhotoLightbox";
import { PhotoThumbs } from "@/components/PhotoThumbs";
import { SavedCard } from "@/components/SavedCard";
import { convertCnyToUsd, convertUsdToCny } from "@/lib/fx";
import { COLORS, KINDS, assertNever, keepSizesForKind, sizeScaleForKind, sizesForKind } from "@/lib/kinds";
import { nextMa, parseHubMa } from "@/lib/mint";
import { normalizeFindCode } from "@/lib/on-hand";
import { computeAutoPrice, DEBOX_LOCKED, MARGIN_FLOOR, TARGET_MARGIN } from "@/lib/pricing";
import type { PriceBreakdown } from "@/lib/pricing";
import type { TaobaoItem } from "@/lib/taobao";
import type { KindCode } from "@/lib/kinds";
import type { MaLookup, Submission, TabId } from "@/lib/types";

type PhotoDraft = {
  id: string;
  file?: File;
  url: string;
};

export function IntakeApp({
  initialFxRate,
  initialFxLabel,
}: {
  initialFxRate: number;
  initialFxLabel: string;
}) {
  const [tab, setTab] = useState<TabId>("create");
  const [kind, setKind] = useState<KindCode>("A");
  const [sizes, setSizes] = useState<string[]>([]);
  const [colors, setColors] = useState<string[]>([]);
  const [colorNote, setColorNote] = useState("");
  const [link, setLink] = useState("");
  const [costUsd, setCostUsd] = useState("");
  const [costCny, setCostCny] = useState("");
  const [sellUsd, setSellUsd] = useState("");
  const [sellCny, setSellCny] = useState("");
  const [photos, setPhotos] = useState<PhotoDraft[]>([]);
  const [lookupMa, setLookupMa] = useState("");
  const [loadedMa, setLoadedMa] = useState<string | null>(null);
  const [lastMa, setLastMa] = useState<string | null>(null);
  const [renameTo, setRenameTo] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<Submission | null>(null);
  const [knownMas, setKnownMas] = useState<string[]>([]);
  const [fxRate] = useState(initialFxRate);
  const [fxLabel] = useState(initialFxLabel);
  // --- Taobao lookup (server-side prefill) ---
  const [tbState, setTbState] = useState<"idle" | "loading" | "ok" | "blocked">("idle");
  const [tbItem, setTbItem] = useState<TaobaoItem | null>(null);
  const [tbReason, setTbReason] = useState("");
  const [sellerColors, setSellerColors] = useState<string[]>([]);
  const [needsResearch, setNeedsResearch] = useState(false);
  // --- Auto-price calculator ---
  const [calcCny, setCalcCny] = useState("");
  const [calcFx, setCalcFx] = useState(String(initialFxRate));
  const [calcDebox, setCalcDebox] = useState("");
  const [autoPrice, setAutoPrice] = useState<PriceBreakdown | null>(null);
  const [findPreview, setFindPreview] = useState<string | null>(null);
  const [findMatches, setFindMatches] = useState<{ ma: string; kind: string; color: string }[]>([]);
  const [findCopied, setFindCopied] = useState<string | null>(null);
  const [findCode, setFindCode] = useState("");
  const [findCard, setFindCard] = useState<MaLookup | null>(null);
  const [findMiss, setFindMiss] = useState(false);
  const [savedRows, setSavedRows] = useState<Submission[]>([]);
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [confirm, setConfirm] = useState<null | { kind: "rename" | "overwrite"; ma: string; next: string | null }>(null);
  const toastSeq = useRef(0);

  function pushToast(text: string, tone: ToastItem["tone"]) {
    const id = (toastSeq.current += 1);
    setToasts((current) => [...current, { id, text, tone }].slice(-4));
  }

  useEffect(() => {
    void refreshMas();
    const ma = new URLSearchParams(window.location.search).get("ma");
    if (!ma) return;
    setTab("edit");
    setLookupMa(ma);
    void loadMa(ma);
  }, []);

  const colorLine = useMemo(() => [...colors, ...sellerColors].join(", "), [colors, sellerColors]);

  const deboxLocked = useMemo(() => kind.toUpperCase() in DEBOX_LOCKED, [kind]);

  const priceBreakdown = useMemo<PriceBreakdown | null>(() => {
    const deboxNum = Number(calcDebox);
    return computeAutoPrice({
      costCny: Number(calcCny),
      fxRate: Number(calcFx),
      kind,
      deboxOverrides:
        !deboxLocked && Number.isFinite(deboxNum) && deboxNum >= 0 && calcDebox.trim() !== ""
          ? { [kind]: deboxNum }
          : undefined,
    });
  }, [calcCny, calcFx, calcDebox, kind, deboxLocked]);

  // Keep the calculator's CNY in sync with the cost field until it computes.
  useEffect(() => {
    setCalcCny((current) => (current === "" ? costCny : current));
  }, [costCny]);

  async function onTaobaoLookup() {
    if (!link.trim()) {
      setError("Dán link Taobao trước nha iu ơi.");
      return;
    }
    setTbState("loading");
    setTbReason("");
    setError(null);
    try {
      const response = await fetch("/api/taobao-lookup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ link }),
      });
      const data = (await response.json()) as {
        ok?: boolean;
        blocked?: boolean;
        reason?: string;
        item?: TaobaoItem;
      };
      if (data.ok && data.item) {
        const item = data.item;
        setTbItem(item);
        setTbState("ok");
        setNeedsResearch(false);
        // Seller SKU colors are seller truth — keep them marked, never translated.
        setSellerColors((current) => {
          const merged = [...current];
          for (const color of item.colors) {
            if (!colors.includes(color) && !merged.includes(color)) merged.push(color);
          }
          return merged;
        });
        // Prefill cost from the seller's list ¥ (promo noted in the panel).
        if (item.listCny) {
          setCostCny(item.listCny);
          const usd = convertCnyToUsd(item.listCny, fxRate);
          if (usd !== null) setCostUsd(usd);
          setCalcCny(item.listCny);
        }
      } else {
        setTbState("blocked");
        setTbReason(data.reason || "Taobao chặn fetch tự động.");
        // Graceful degrade: keep what the user typed, flag for manual research.
        setNeedsResearch(true);
      }
    } catch {
      setTbState("blocked");
      setTbReason("Không gọi được server, thử lại nha.");
      setNeedsResearch(true);
    }
  }

  function onUseAutoPrice() {
    if (!priceBreakdown) return;
    const sell = String(priceBreakdown.sellUsd);
    setSellUsd(sell);
    const cny = convertUsdToCny(sell, fxRate);
    if (cny !== null) setSellCny(cny);
    setAutoPrice(priceBreakdown);
  }

  function resetForm() {
    setKind("A");
    setSizes([]);
    setColors([]);
    setSellerColors([]);
    setColorNote("");
    setLink("");
    setCostUsd("");
    setCostCny("");
    setSellUsd("");
    setSellCny("");
    setPhotos([]);
    setLoadedMa(null);
    setRenameTo("");
    setError(null);
    setTbState("idle");
    setTbItem(null);
    setTbReason("");
    setNeedsResearch(false);
    setCalcCny("");
    setCalcFx(String(initialFxRate));
    setCalcDebox("");
    setAutoPrice(null);
  }

  function switchTab(next: TabId) {
    setTab(next);
    setError(null);
    setFindMatches([]);
    setFindPreview(null);
    setFindMiss(false);
    setFindCard(null);
    if (next === "create") resetForm();
    if (next === "edit") {
      const reopen = lastMa || lookupMa.trim();
      if (reopen) {
        setLookupMa(reopen);
        void loadMa(reopen);
      } else {
        resetForm();
      }
    }
  }

  async function refreshMas(): Promise<string[]> {
    try {
      const response = await fetch("/api/submissions");
      const data = (await response.json()) as { submissions?: Submission[] };
      const rows = data.submissions ?? [];
      setSavedRows(rows);
      const mas = rows.map((row) => String(row.ma ?? "")).filter(Boolean);
      setKnownMas(mas);
      return mas;
    } catch {
      return knownMas;
    }
  }

  async function loadMa(raw: string): Promise<Submission | null> {
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`/api/submissions/${encodeURIComponent(raw.trim())}`);
      const data = (await response.json()) as { submission?: Submission; error?: string };
      if (!response.ok || !data.submission) {
        setError(data.error || "Không tìm thấy mã này 🥺");
        setLoadedMa(null);
        return null;
      }
      applySubmission(data.submission);
      setLastMa(data.submission.ma);
      await refreshMas();
      return data.submission;
    } catch {
      setError("Mạng hơi lag, thử lại nha.");
      return null;
    } finally {
      setBusy(false);
    }
  }

  function applySubmission(item: Submission) {
    setLoadedMa(item.ma);
    setLookupMa(item.ma);
    setKind(item.kind);
    setSizes(item.size.split(/[\s,]+/).filter(Boolean));
    const snapshotColors = item.taobao_snapshot?.colors ?? [];
    const allColors = item.color
      .split(",")
      .map((part) => part.trim())
      .filter(Boolean);
    setSellerColors(allColors.filter((color) => snapshotColors.includes(color)));
    setColors(allColors.filter((color) => !snapshotColors.includes(color)));
    setColorNote(item.color_note);
    setLink(item.link);
    setCostUsd(item.cost_usd);
    setCostCny(item.cost_cny);
    setSellUsd(item.sell_usd);
    setSellCny(item.sell_cny);
    setNeedsResearch(Boolean(item.needs_research));
    setTbItem(item.taobao_snapshot ?? null);
    setTbState(item.taobao_snapshot ? "ok" : "idle");
    setAutoPrice(item.auto_price ?? null);
    setCalcCny(item.cost_cny);
    setPhotos(
      (item.photo_paths ?? []).map((rel) => ({
        id: `keep:${rel}`,
        url: `/api/photos/${rel}`,
      })),
    );
    setRenameTo("");
  }

  async function save(renameMa?: string | null, editingMa?: string | null): Promise<boolean> {
    setError(null);
    setBusy(true);
    try {
      const form = new FormData();
      form.set("kind", kind);
      form.set("prefix", kind);
      form.set("size", sizes.join(" "));
      form.set("link", link);
      form.set("cost_usd", costUsd);
      form.set("cost_cny", costCny);
      form.set("cost_currency", costUsd ? "USD" : costCny ? "CNY" : "USD");
      form.set("sell_usd", sellUsd);
      form.set("sell_cny", sellCny);
      form.set("sell_currency", sellUsd ? "USD" : sellCny ? "CNY" : "USD");
      form.set("color", colorLine);
      form.set("color_note", colorNote);
      form.set("pieces", JSON.stringify([]));
      form.set("needs_research", needsResearch ? "1" : "");
      form.set("taobao_snapshot", tbItem ? JSON.stringify(tbItem) : "");
      form.set("auto_price", autoPrice ? JSON.stringify(autoPrice) : "");
      form.set("keep_photos", JSON.stringify(photos.filter((p) => p.id.startsWith("keep:")).map((p) => p.id.slice(5))));
      form.set("save", "1");
      if (renameMa) form.set("new_ma", renameMa);
      for (const photo of photos) {
        if (photo.file) form.append("photos", photo.file);
      }
      const existing = editingMa || (tab === "edit" ? loadedMa : null);
      const url = existing ? `/api/submissions/${encodeURIComponent(existing)}` : "/api/submissions";
      const response = await fetch(url, { method: existing ? "PATCH" : "POST", body: form });
      const data = (await response.json()) as { submission?: Submission; error?: string };
      if (!response.ok || !data.submission) {
        setError(data.error || "Chưa nhận được mã. Thử lại nha 🥺");
        return false;
      }
      setSaved(data.submission);
      pushToast(`Đã lưu ${data.submission.ma}`, "ok");
      setLoadedMa(data.submission.ma);
      setLookupMa(data.submission.ma);
      setLastMa(data.submission.ma);
      if (tab === "create") resetForm();
      else applySubmission(data.submission);
      await refreshMas();
      return true;
    } catch {
      setError("Chưa gửi được. Kiểm tra mạng rồi thử lại 💕");
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function onSaveClick() {
    let current = loadedMa;
    if (tab === "edit" && !current && lookupMa.trim()) {
      const loaded = await loadMa(lookupMa);
      current = loaded?.ma ?? null;
    }
    if (tab === "edit" && !current) return;
    if (tab === "edit" && current) {
      const next = renameTo.trim();
      setConfirm({ kind: next ? "rename" : "overwrite", ma: current, next: next || null });
      return;
    }
    await save(null, current);
  }

  async function confirmSave() {
    if (!confirm) return;
    const pending = confirm;
    const ok = await save(pending.kind === "rename" ? pending.next : null, pending.ma);
    if (ok) setConfirm(null);
  }

  function toggleSize(value: string) { setSizes((current) => current.includes(value) ? current.filter((s) => s !== value) : [...current, value]); } function onKind(next: KindCode) {
    setKind(next);
    setSizes((current) => keepSizesForKind(current, next));
    if (tab === "edit" && loadedMa) {
      const current = parseHubMa(loadedMa)?.kind;
      if (current && current !== next) {
        setRenameTo(nextMa(next, knownMas));
      }
    }
  }

  async function onFindCode() {
    const code = normalizeFindCode(findCode);
    setFindCode(code);
    setFindMiss(false);
    setFindCard(null);
    if (!code) {
      setFindMiss(true);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`/api/ma/${encodeURIComponent(code)}`);
      const data = (await response.json()) as MaLookup & { error?: string };
      if (!response.ok || !data.staged) {
        setFindMiss(true);
        return;
      }
      setFindCard({
        code: data.code,
        staged: data.staged,
        on_hand: data.on_hand ?? [],
        staged_only: Boolean(data.staged_only ?? (data.on_hand ?? []).length === 0),
      });
    } catch {
      setError("Mạng hơi lag, thử lại nha.");
    } finally {
      setBusy(false);
    }
  }

  async function onFindPhoto(file: File) {
    setError(null);
    setFindCopied(null);
    const preview = URL.createObjectURL(file);
    setFindPreview(preview);
    setBusy(true);
    try {
      const form = new FormData();
      form.set("photo", file);
      const response = await fetch("/api/find-ma", { method: "POST", body: form });
      const data = (await response.json()) as {
        matches?: { ma: string; kind: string; color: string }[];
        error?: string;
      };
      if (!response.ok) {
        setError(data.error || "Không thấy mã khớp");
        setFindMatches([]);
        return;
      }
      setFindMatches(data.matches ?? []);
    } catch {
      setError("Chưa gửi được. Kiểm tra mạng rồi thử lại 💕");
    } finally {
      setBusy(false);
    }
  }

  const canSave = tab === "create" || Boolean(loadedMa || lookupMa.trim());

  return (
    <main
      data-testid="intake-shell"
      className="relative z-10 mx-auto flex min-h-dvh w-full max-w-md flex-col px-4 py-6 md:max-w-2xl md:px-6 lg:max-w-5xl lg:px-10 lg:py-12 xl:max-w-6xl"
    >
      <div className="mb-4 flex items-end justify-between gap-3 border-b border-[#eadfdc] pb-4">
        <BrandHeader />
        <button
          type="button"
          className="inline-flex min-h-11 shrink-0 items-center rounded-full px-4 text-sm font-semibold text-[#5c3d48] ring-1 ring-[#eadfdc]"
          onClick={() => switchTab("create")}
        >
          Món mới
        </button>
      </div>
      <div
        data-testid="intake-tabs"
        role="tablist"
        aria-label="Intake"
        className="adm-scroll mb-4 flex gap-1 overflow-x-auto rounded-full bg-white/80 p-1 ring-1 ring-[#eadfdc] lg:mx-auto lg:mb-6 lg:w-full lg:max-w-xl"
      >
        <TabButton id="create" current={tab} onClick={switchTab} mobile="Món mới" desktop="Món mới" />
        <TabButton id="edit" current={tab} onClick={switchTab} mobile="Sửa mã" desktop="Sửa theo mã" />
        <TabButton id="find" current={tab} onClick={switchTab} mobile="Tìm mã" desktop="Tìm mã · Find" />
        <TabButton
          id="ask"
          current={tab}
          onClick={switchTab}
          mobile="Mini Boss"
          desktop="Hỏi Mini Boss · Ask"
          ariaLabel="Hỏi Mini Boss · Ask"
        />
      </div>
      <section className="flex flex-1 flex-col rounded-3xl bg-card p-4 ring-1 ring-[#eadfdc] lg:p-8">
        {renderTab({
          tab,
          kind,
          onKind,
          sizes,
          setSizes,
          colors,
          setColors,
          colorNote,
          setColorNote,
          link,
          setLink,
          costUsd,
          setCostUsd,
          costCny,
          setCostCny,
          sellUsd,
          setSellUsd,
          sellCny,
          setSellCny,
          photos,
          setPhotos,
          lookupMa,
          setLookupMa,
          loadedMa,
          renameTo,
          setRenameTo,
          loadMa,
          onSaveClick,
          canSave,
          busy,
          fxRate,
          fxLabel,
          tbState,
          tbItem,
          tbReason,
          onTaobaoLookup,
          sellerColors,
          setSellerColors,
          needsResearch,
          setNeedsResearch,
          toggleSize,
          calcCny,
          setCalcCny,
          calcFx,
          setCalcFx,
          calcDebox,
          setCalcDebox,
          deboxLocked,
          priceBreakdown,
          onUseAutoPrice,
          findPreview,
          findMatches,
          findCopied,
          setFindCopied,
          onFindPhoto,
          findCode,
          setFindCode,
          onFindCode,
          findMiss,
          findBusy: busy,
        })}
        {error ? (
          <p data-testid="intake-error" role="alert" className="mt-4 text-center text-sm text-[#9b2c2c]">
            {error}
          </p>
        ) : null}
      </section>
      <SavedList
        rows={savedRows}
        onOpen={(ma) => {
          setTab("edit");
          setLookupMa(ma);
          void loadMa(ma);
        }}
        onCreate={() => switchTab("create")}
      />
      {confirm ? (
        <ConfirmDialog
          title={confirm.kind === "rename" ? `Đổi mã ${confirm.ma}?` : `Lưu đè ${confirm.ma}?`}
          body={
            confirm.kind === "rename"
              ? `${confirm.ma} sẽ thành ${confirm.next ?? ""}.`
              : `Ghi đè món ${confirm.ma} bằng form này.`
          }
          confirmLabel={confirm.kind === "rename" ? "Đổi mã" : "Lưu đè"}
          danger={confirm.kind === "rename"}
          pending={busy}
          onCancel={() => setConfirm(null)}
          onConfirm={() => void confirmSave()}
        />
      ) : null}
      <ToastStack toasts={toasts} onDismiss={(id) => setToasts((current) => current.filter((toast) => toast.id !== id))} />
      <p className="mt-4 text-center text-xs text-rose-700/70">
        <a className="inline-flex min-h-11 items-center underline-offset-2 hover:underline" href="/admin">
          Kit export CSV
        </a>
        <span className="mx-1">·</span>
        <a className="inline-flex min-h-11 items-center underline-offset-2 hover:underline" href="/admin/shop">
          Shop tools
        </a>
        <span className="mx-1">· Boss one-pager trong README / BOSS.md</span>
      </p>
      <SavedCard result={saved} onClose={() => setSaved(null)} />
      <FindMaCard result={findCard} onClose={() => setFindCard(null)} />
    </main>
  );
}

function renderTab(props: {
  tab: TabId;
  kind: KindCode;
  onKind: (kind: KindCode) => void;
  sizes: string[];
  setSizes: (value: string[]) => void;
  colors: string[];
  setColors: (value: string[]) => void;
  colorNote: string;
  setColorNote: (value: string) => void;
  link: string;
  setLink: (value: string) => void;
  costUsd: string;
  setCostUsd: (value: string) => void;
  costCny: string;
  setCostCny: (value: string) => void;
  sellUsd: string;
  setSellUsd: (value: string) => void;
  sellCny: string;
  setSellCny: (value: string) => void;
  photos: PhotoDraft[];
  setPhotos: (value: PhotoDraft[]) => void;
  lookupMa: string;
  setLookupMa: (value: string) => void;
  loadedMa: string | null;
  renameTo: string;
  setRenameTo: (value: string) => void;
  loadMa: (ma: string) => Promise<Submission | null>;
  onSaveClick: () => Promise<void>;
  canSave: boolean;
  busy: boolean;
  fxRate: number;
  fxLabel: string;
  tbState: "idle" | "loading" | "ok" | "blocked";
  tbItem: TaobaoItem | null;
  tbReason: string;
  onTaobaoLookup: () => void;
  sellerColors: string[];
  setSellerColors: (value: string[]) => void;
  needsResearch: boolean;
  setNeedsResearch: (value: boolean) => void;
  toggleSize: (value: string) => void;
  calcCny: string;
  setCalcCny: (value: string) => void;
  calcFx: string;
  setCalcFx: (value: string) => void;
  calcDebox: string;
  setCalcDebox: (value: string) => void;
  deboxLocked: boolean;
  priceBreakdown: PriceBreakdown | null;
  onUseAutoPrice: () => void;
  findPreview: string | null;
  findMatches: { ma: string; kind: string; color: string }[];
  findCopied: string | null;
  setFindCopied: (value: string | null) => void;
  onFindPhoto: (file: File) => Promise<void>;
  findCode: string;
  setFindCode: (value: string) => void;
  onFindCode: () => Promise<void>;
  findMiss: boolean;
  findBusy: boolean;
}) {
  switch (props.tab) {
    case "ask":
      return <AskPanel />;
    case "find":
      return (
        <FindPanel
          preview={props.findPreview}
          matches={props.findMatches}
          copied={props.findCopied}
          setCopied={props.setFindCopied}
          onPhoto={props.onFindPhoto}
          code={props.findCode}
          setCode={props.setFindCode}
          onFindCode={props.onFindCode}
          miss={props.findMiss}
          busy={props.findBusy}
        />
      );
    case "create":
    case "edit":
      return <ItemForm {...props} />;
    default: {
      const _never: never = props.tab;
      return assertNever(_never, "Unknown tab");
    }
  }
}

function TabButton({
  id,
  current,
  onClick,
  mobile,
  desktop,
  ariaLabel,
}: {
  id: TabId;
  current: TabId;
  onClick: (id: TabId) => void;
  mobile: string;
  desktop: string;
  ariaLabel?: string;
}) {
  const active = current === id;
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      data-testid={`tab-${id}`}
      aria-label={ariaLabel}
      className={`inline-flex min-h-11 min-w-11 shrink-0 items-center justify-center rounded-full px-3 text-[13px] font-semibold ${
        active ? "bg-white text-[#3c2a2e] shadow-sm ring-1 ring-[#eadfdc]" : "text-[#7d5360]"
      }`}
      onClick={() => onClick(id)}
    >
      <span className="lg:hidden">{mobile}</span>
      <span className="hidden lg:inline">{desktop}</span>
    </button>
  );
}

function ItemForm(props: {
  tab: TabId;
  kind: KindCode;
  onKind: (kind: KindCode) => void;
  sizes: string[];
  setSizes: (value: string[]) => void;
  colors: string[];
  setColors: (value: string[]) => void;
  colorNote: string;
  setColorNote: (value: string) => void;
  link: string;
  setLink: (value: string) => void;
  costUsd: string;
  setCostUsd: (value: string) => void;
  costCny: string;
  setCostCny: (value: string) => void;
  sellUsd: string;
  setSellUsd: (value: string) => void;
  sellCny: string;
  setSellCny: (value: string) => void;
  photos: PhotoDraft[];
  setPhotos: (value: PhotoDraft[]) => void;
  lookupMa: string;
  setLookupMa: (value: string) => void;
  loadedMa: string | null;
  renameTo: string;
  setRenameTo: (value: string) => void;
  loadMa: (ma: string) => Promise<Submission | null>;
  onSaveClick: () => Promise<void>;
  canSave: boolean;
  busy: boolean;
  fxRate: number;
  fxLabel: string;
  tbState: "idle" | "loading" | "ok" | "blocked";
  tbItem: TaobaoItem | null;
  tbReason: string;
  onTaobaoLookup: () => void;
  sellerColors: string[];
  setSellerColors: (value: string[]) => void;
  needsResearch: boolean;
  setNeedsResearch: (value: boolean) => void;
  toggleSize: (value: string) => void;
  calcCny: string;
  setCalcCny: (value: string) => void;
  calcFx: string;
  setCalcFx: (value: string) => void;
  calcDebox: string;
  setCalcDebox: (value: string) => void;
  deboxLocked: boolean;
  priceBreakdown: PriceBreakdown | null;
  onUseAutoPrice: () => void;
}) {
  return (
    <div data-testid="intake-grid" className="flex flex-col lg:grid lg:grid-cols-2 lg:gap-x-10">
      <div>
        {props.tab === "edit" ? (
          <fieldset className="mb-4">
            <label className="mb-2 block text-sm font-medium" htmlFor="lookup-ma">
              Mã
            </label>
            <div className="flex gap-2">
              <input
                id="lookup-ma"
                data-testid="lookup-ma"
                value={props.lookupMa}
                onChange={(event) => props.setLookupMa(event.target.value)}
                placeholder="A01"
                className="h-11 flex-1 rounded-xl bg-white px-3 ring-1 ring-rose-100"
              />
              <button
                type="button"
                data-testid="lookup-load"
                className="h-11 rounded-full bg-white px-4 text-sm font-semibold text-rose-800 ring-1 ring-rose-100"
                onClick={() => void props.loadMa(props.lookupMa)}
              >
                Mở
              </button>
            </div>
            {props.loadedMa ? (
              <p className="mt-2 text-xs text-rose-700">Đang sửa {props.loadedMa}</p>
            ) : (
              <p className="mt-2 text-xs text-rose-700/70">Gõ mã như A01 để tìm nha iu ơi.</p>
            )}
            <label className="mt-3 mb-1 block text-xs font-medium" htmlFor="rename-ma">
              Đổi mã · Change code
            </label>
            <input
              id="rename-ma"
              data-testid="rename-ma"
              value={props.renameTo}
              onChange={(event) => props.setRenameTo(event.target.value)}
              placeholder="P hoặc P10"
              className="h-11 w-full rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
          </fieldset>
        ) : null}
        <fieldset className="mb-4">
          <label className="mb-2 block text-sm font-medium">Loại đồ · Type</label>
          <div className="flex flex-wrap gap-2">
            {KINDS.map((item) => (
              <button
                key={item.code}
                type="button"
                data-testid={`kind-${item.code}`}
                className={`inline-flex min-h-11 min-w-11 items-center rounded-full px-3 py-2 text-sm font-semibold ring-1 ${
                  props.kind === item.code
                    ? "bg-[#f3e6e2] text-[#3c2a2e] ring-[#e6d0ca]"
                    : "bg-white text-[#5c3d48] ring-[#eadfdc]"
                }`}
                onClick={() => props.onKind(item.code)}
              >
                {item.label}
                <span className="ml-1 text-[11px] opacity-70">{item.hint}</span>
              </button>
            ))}
          </div>
        </fieldset>
        <fieldset className="mb-4" data-testid="piece-board">
          <label className="mb-2 block text-sm font-medium">
            Ảnh + màu <span className="font-normal text-rose-700/60">(tuỳ chọn)</span>
          </label>
          <label className="mt-3 flex min-h-28 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-rose-200 bg-white text-center text-xs text-rose-700">
            <span className="text-lg">♡</span>
            Thêm ảnh
            <input
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={(event) => {
                const files = [...(event.target.files ?? [])];
                props.setPhotos([
                  ...props.photos,
                  ...files.map((file) => ({
                    id: `new:${file.name}:${file.size}:${file.lastModified}`,
                    file,
                    url: URL.createObjectURL(file),
                  })),
                ]);
              }}
            />
          </label>
          {props.photos.length ? (
            <PhotoThumbs
              photos={props.photos.map((photo) => photo.url)}
              layout="grid"
              testId="form-photos"
              thumbTestIdPrefix="form-photo"
              className="mt-3"
            />
          ) : null}
          <div className="mt-4" data-testid="available-colors">
            <label className="mb-2 block text-sm font-medium">
              🎨 Màu có sẵn <span className="font-normal text-rose-700/60">(tuỳ chọn)</span>
            </label>
            <div className="flex flex-wrap gap-1.5">
              {COLORS.map((chip) => {
                const on = props.colors.includes(chip.vi);
                return (
                  <button
                    key={chip.code}
                    type="button"
                    data-testid={`color-chip-${chip.code}`}
                    aria-pressed={on}
                    className={`inline-flex min-h-11 min-w-11 items-center rounded-full px-3 text-xs font-semibold ring-1 ${
                      on ? "bg-[#f3e6e2] text-[#3c2a2e] ring-[#e6d0ca]" : "bg-white text-[#5c3d48] ring-[#eadfdc]"
                    }`}
                    onClick={() =>
                      props.setColors(
                        on ? props.colors.filter((c) => c !== chip.vi) : [...props.colors, chip.vi],
                      )
                    }
                  >
                    {chip.vi}
                  </button>
                );
              })}
            </div>
            <label className="mt-3 mb-1 block text-sm font-medium" htmlFor="color-note">
              📝 Ghi chú màu <span className="font-normal text-rose-700/60">(tuỳ chọn)</span>
            </label>
            <input
              id="color-note"
              data-testid="color-note"
              value={props.colorNote}
              onChange={(event) => props.setColorNote(event.target.value)}
              className="h-11 w-full rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
          </div>
        </fieldset>
      </div>
      <div>
        <fieldset className="mb-4" data-testid="size-board">
          <label className="mb-2 block text-sm font-medium">
            {sizeScaleForKind(props.kind) === "shoe"
              ? "Size giày Á châu · 35–41 (tuỳ chọn)"
              : "Size (tuỳ chọn)"}
          </label>
          <div className="flex flex-wrap gap-1.5" data-testid="size-options">
            {sizesForKind(props.kind).map((size) => {
              const on = props.sizes.includes(size);
              return (
                <button
                  key={size}
                  type="button"
                  data-testid={`size-${size}`}
                  className={`inline-flex min-h-11 min-w-11 items-center justify-center rounded-full px-3 text-sm font-semibold ring-1 ${
                    on ? "bg-[#f3e6e2] text-[#3c2a2e] ring-[#e6d0ca]" : "bg-white text-[#5c3d48] ring-[#eadfdc]"
                  }`}
                  onClick={() =>
                    props.setSizes(on ? props.sizes.filter((s) => s !== size) : [...props.sizes, size])
                  }
                >
                  {size}
                </button>
              );
            })}
          </div>
        </fieldset>
        <fieldset className="mb-4">
          <label className="mb-2 block text-sm font-medium">Giá gốc / cost (tuỳ chọn)</label>
          <div className="grid grid-cols-2 gap-2">
            <input
              data-testid="cost-cny"
              value={props.costCny}
              onChange={(event) => {
                const value = event.target.value;
                props.setCostCny(value);
                const usd = convertCnyToUsd(value, props.fxRate);
                if (usd !== null) props.setCostUsd(usd);
              }}
              placeholder="¥ CNY"
              className="h-11 rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
            <input
              data-testid="cost-usd"
              value={props.costUsd}
              onChange={(event) => {
                const value = event.target.value;
                props.setCostUsd(value);
                const cny = convertUsdToCny(value, props.fxRate);
                if (cny !== null) props.setCostCny(cny);
              }}
              placeholder="$ USD"
              className="h-11 rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
          </div>
        </fieldset>
        <fieldset className="mb-4">
          <label className="mb-2 block text-sm font-medium">Giá bán / sell (tuỳ chọn)</label>
          <div className="grid grid-cols-2 gap-2">
            <input
              data-testid="sell-cny"
              value={props.sellCny}
              onChange={(event) => {
                const value = event.target.value;
                props.setSellCny(value);
                const usd = convertCnyToUsd(value, props.fxRate);
                if (usd !== null) props.setSellUsd(usd);
              }}
              placeholder="¥ CNY"
              className="h-11 rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
            <input
              data-testid="sell-usd"
              value={props.sellUsd}
              onChange={(event) => {
                const value = event.target.value;
                props.setSellUsd(value);
                const cny = convertUsdToCny(value, props.fxRate);
                if (cny !== null) props.setSellCny(cny);
              }}
              placeholder="$ USD"
              className="h-11 rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
          </div>
        </fieldset>
        <p className="mb-4 text-center text-[11px] text-rose-700/70">{props.fxLabel}</p>
        <PricePanel
          calcCny={props.calcCny}
          setCalcCny={props.setCalcCny}
          calcFx={props.calcFx}
          setCalcFx={props.setCalcFx}
          calcDebox={props.calcDebox}
          setCalcDebox={props.setCalcDebox}
          deboxLocked={props.deboxLocked}
          kind={props.kind}
          breakdown={props.priceBreakdown}
          onUse={props.onUseAutoPrice}
        />
        <fieldset className="mb-5">
          <label className="mb-2 block text-sm font-medium" htmlFor="link">
            Link shop / Taobao <span className="font-normal text-rose-700/60">(tuỳ chọn)</span>
          </label>
          <input
            id="link"
            data-testid="shop-link"
            value={props.link}
            onChange={(event) => props.setLink(event.target.value)}
            placeholder="https://e.tb.cn/... hoặc dán cả đoạn share"
            className="h-11 w-full rounded-xl bg-white px-3 ring-1 ring-rose-100"
          />
        </fieldset>
        <TaobaoPanel
          state={props.tbState}
          item={props.tbItem}
          reason={props.tbReason}
          onLookup={props.onTaobaoLookup}
          sellerColors={props.sellerColors}
          onRemoveSellerColor={(color) =>
            props.setSellerColors(props.sellerColors.filter((c) => c !== color))
          }
          sizes={props.sizes}
          toggleSize={props.toggleSize}
        />
        {props.needsResearch ? (
          <p data-testid="needs-research-banner" className="mb-5 rounded-2xl bg-amber-50 p-3 text-xs text-amber-800 ring-1 ring-amber-200">
            ⚠ Submission này gắn “cần nghiên cứu tay” (Taobao chặn fetch).
            <button
              type="button"
              className="ml-2 font-semibold underline"
              onClick={() => props.setNeedsResearch(false)}
            >
              Bỏ đánh dấu
            </button>
          </p>
        ) : null}
        <StatusChips
          photos={props.photos.length}
          sizes={props.sizes.length}
          hasPrice={Boolean(props.sellUsd.trim() || props.sellCny.trim())}
          needsResearch={props.needsResearch}
          belowFloor={props.priceBreakdown ? !props.priceBreakdown.captionEligible : false}
        />
        <button
          type="button"
          data-testid="save-mint"
          disabled={props.busy || !props.canSave}
          className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-full bg-primary text-base font-bold text-primary-foreground disabled:opacity-50 lg:h-14 lg:text-lg"
          onClick={() => void props.onSaveClick()}
        >
          {props.busy ? <span className="adm-spin" aria-hidden /> : null}
          {props.busy
            ? "Đang lưu…"
            : props.tab === "edit"
              ? "Lưu thay đổi · Keep same mã"
              : "Lưu & lấy mã · Mint code"}
        </button>
      </div>
    </div>
  );
}

function TaobaoPanel({
  state,
  item,
  reason,
  onLookup,
  sellerColors,
  onRemoveSellerColor,
  sizes,
  toggleSize,
}: {
  state: "idle" | "loading" | "ok" | "blocked";
  item: TaobaoItem | null;
  reason: string;
  onLookup: () => void;
  sellerColors: string[];
  onRemoveSellerColor: (color: string) => void;
  sizes: string[];
  toggleSize: (value: string) => void;
}) {
  return (
    <div data-testid="taobao-panel" className="mb-5 rounded-2xl bg-white p-3 ring-1 ring-rose-100">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium">🔍 Tra link Taobao</p>
        <button
          type="button"
          data-testid="taobao-lookup"
          onClick={onLookup}
          disabled={state === "loading"}
          className="inline-flex min-h-11 items-center rounded-full bg-white px-4 text-sm font-semibold text-[#5c3d48] ring-1 ring-[#eadfdc] disabled:opacity-50"
        >
          {state === "loading" ? "Đang tra…" : "Tra link"}
        </button>
      </div>
      <p className="mt-1 text-[11px] text-rose-700/70">
        Server tự đọc listing: màu seller, size, giá ¥, ảnh. Taobao hay chặn — khi chặn thì nhập tay nha.
      </p>
      {state === "blocked" ? (
        <p data-testid="taobao-blocked" className="mt-2 rounded-xl bg-amber-50 p-2 text-xs text-amber-800 ring-1 ring-amber-200">
          ⚠ {reason} Giữ nguyên những gì đã nhập — submission được gắn “cần nghiên cứu tay”.
        </p>
      ) : null}
      {state === "ok" && item ? (
        <div data-testid="taobao-result" className="mt-2 space-y-2">
          {item.title ? <p className="text-xs font-medium text-rose-900">{item.title}</p> : null}
          <p className="text-xs text-rose-800">
            Giá list: {item.listCny ? <span className="font-bold">¥{item.listCny}</span> : "không thấy"}
            {item.promoCny ? (
              <span className="ml-2">· 优惠价 <span className="font-bold">¥{item.promoCny}</span></span>
            ) : null}
            {item.promoNote === "pre_promo" ? (
              <span className="ml-2 text-amber-700">(giá 优惠前 — chưa trừ khuyến mãi)</span>
            ) : null}
          </p>
          {sellerColors.length ? (
            <div>
              <p className="text-[11px] font-medium text-rose-700">
                🏷 Màu của seller <span className="font-normal">(seller truth — không dịch)</span>
              </p>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {sellerColors.map((color) => (
                  <span
                    key={color}
                    className="inline-flex items-center gap-1 rounded-full bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-900 ring-1 ring-rose-200"
                  >
                    🏷 {color}
                    <button
                      type="button"
                      aria-label={`Bỏ màu ${color}`}
                      className="text-rose-500"
                      onClick={() => onRemoveSellerColor(color)}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-xs text-rose-700/70">Không đọc được màu seller từ link này.</p>
          )}
          {item.sizeAxes.map((axis) => (
            <div key={axis.name}>
              <p className="text-[11px] font-medium text-rose-700">
                📐 {axis.name} <span className="font-normal">(seller)</span>
              </p>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {axis.values.map((value) => {
                  const on = sizes.includes(value);
                  return (
                    <button
                      key={value}
                      type="button"
                      onClick={() => toggleSize(value)}
                      aria-pressed={on}
                      className={`inline-flex min-h-11 min-w-11 items-center justify-center rounded-full px-3 text-xs font-semibold ring-1 ${
                        on ? "bg-[#f3e6e2] text-[#3c2a2e] ring-[#e6d0ca]" : "bg-white text-[#5c3d48] ring-[#eadfdc]"
                      }`}
                    >
                      {value}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
          {item.gallery.length ? (
            <div>
              <p className="text-[11px] font-medium text-rose-700">🖼 Ảnh từ Taobao ({item.gallery.length})</p>
              <div className="mt-1 flex gap-1.5 overflow-x-auto">
                {item.gallery.slice(0, 8).map((src) => (
                  <img key={src} src={src} alt="" loading="lazy" className="h-16 w-16 rounded-lg object-cover ring-1 ring-rose-100" />
                ))}
              </div>
              <p className="mt-1 text-[11px] text-rose-700/70">
                Link ảnh đã lưu kèm submission để bước sau kéo về.
              </p>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function PricePanel({
  calcCny,
  setCalcCny,
  calcFx,
  setCalcFx,
  calcDebox,
  setCalcDebox,
  deboxLocked,
  kind,
  breakdown,
  onUse,
}: {
  calcCny: string;
  setCalcCny: (value: string) => void;
  calcFx: string;
  setCalcFx: (value: string) => void;
  calcDebox: string;
  setCalcDebox: (value: string) => void;
  deboxLocked: boolean;
  kind: string;
  breakdown: PriceBreakdown | null;
  onUse: () => void;
}) {
  return (
    <div data-testid="price-panel" className="mb-5 rounded-2xl bg-white p-3 ring-1 ring-rose-100">
      <p className="text-sm font-medium">💰 Tính giá tự động <span className="font-normal text-rose-700/60">(margin {Math.round(TARGET_MARGIN * 100)}%)</span></p>
      <div className="mt-2 grid grid-cols-3 gap-2">
        <label className="block">
          <span className="mb-1 block text-[11px] text-rose-700">Giá vốn ¥</span>
          <input
            data-testid="calc-cny"
            value={calcCny}
            onChange={(event) => setCalcCny(event.target.value)}
            placeholder="¥"
            inputMode="decimal"
            className="h-11 w-full rounded-xl bg-[oklch(0.995_0.01_50)] px-2 text-base ring-1 ring-rose-100 md:text-sm"
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-[11px] text-rose-700">Tỷ giá</span>
          <input
            data-testid="calc-fx"
            value={calcFx}
            onChange={(event) => setCalcFx(event.target.value)}
            placeholder="6.723"
            inputMode="decimal"
            className="h-11 w-full rounded-xl bg-[oklch(0.995_0.01_50)] px-2 text-base ring-1 ring-rose-100 md:text-sm"
          />
        </label>
        <label className="block">
          <span className="mb-1 block text-[11px] text-rose-700">
            Debox $ {deboxLocked ? "🔒" : ""}
          </span>
          <input
            data-testid="calc-debox"
            value={deboxLocked ? "7.50" : calcDebox}
            onChange={(event) => setCalcDebox(event.target.value)}
            disabled={deboxLocked}
            placeholder="$0"
            inputMode="decimal"
            className="h-11 w-full rounded-xl bg-[oklch(0.995_0.01_50)] px-2 text-base ring-1 ring-rose-100 disabled:opacity-60 md:text-sm"
          />
        </label>
      </div>
      <p className="mt-1 text-[11px] text-rose-700/70">
        {deboxLocked
          ? `Debox ${kind} cố định $7.50 (bảng khoá V/Q/D).`
          : "Debox các loại khác mặc định $0 — sửa được."}{" "}
        Giá bán = ceil(giá vốn $ ÷ {1 - TARGET_MARGIN}).
      </p>
      {breakdown ? (
        <div data-testid="price-breakdown" className="mt-2 rounded-xl bg-rose-50 p-2 text-xs text-rose-900 ring-1 ring-rose-100">
          <p>Giá vốn (landed): <span className="font-bold">${breakdown.landedUsd.toFixed(2)}</span>
            <span className="text-rose-700/70"> = ¥{calcCny} ÷ {calcFx} + debox ${breakdown.deboxUsd.toFixed(2)}</span>
          </p>
          <p className="mt-1">Giá bán gợi ý: <span className="text-sm font-bold">${breakdown.sellUsd}</span>
            <span className="text-rose-700/70"> · lãi ${breakdown.marginUsd.toFixed(2)} ({(breakdown.marginPct * 100).toFixed(1)}%)</span>
          </p>
          {breakdown.captionEligible ? (
            <p className="mt-1 font-semibold text-[#246044]">✓ Đủ {Math.round(MARGIN_FLOOR * 100)}% — caption sẽ hiện giá.</p>
          ) : (
            <p className="mt-1 font-semibold text-[#8a5a12]">⚠ Dưới {Math.round(MARGIN_FLOOR * 100)}% — caption sẽ là “Inbox giá”.</p>
          )}
          <button
            type="button"
            data-testid="price-use"
            onClick={onUse}
            className="mt-2 inline-flex min-h-11 w-full items-center justify-center rounded-full bg-white text-sm font-bold text-[#5c3d48] ring-1 ring-[#eadfdc]"
          >
            Dùng giá ${breakdown.sellUsd}
          </button>
        </div>
      ) : (
        <p className="mt-2 text-xs text-rose-700/70">Nhập giá vốn ¥ và tỷ giá để tính nha.</p>
      )}
    </div>
  );
}

function FindPreview({ src }: { src: string }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        data-testid="find-preview-thumb"
        aria-label="Xem ảnh lớn"
        className="mb-2"
        onClick={() => setOpen(true)}
      >
        <img src={src} alt="" className="h-28 rounded-xl object-cover" />
      </button>
      <PhotoLightbox src={open ? src : null} onClose={() => setOpen(false)} />
    </>
  );
}

function FindPanel({
  preview,
  matches,
  copied,
  setCopied,
  onPhoto,
  code,
  setCode,
  onFindCode,
  miss,
  busy,
}: {
  preview: string | null;
  matches: { ma: string; kind: string; color: string }[];
  copied: string | null;
  setCopied: (value: string | null) => void;
  onPhoto: (file: File) => Promise<void>;
  code: string;
  setCode: (value: string) => void;
  onFindCode: () => Promise<void>;
  miss: boolean;
  busy: boolean;
}) {
  return (
    <div data-testid="find-ma" className="space-y-5">
      <form
        data-testid="find-code-box"
        className="rounded-2xl bg-white p-3 ring-1 ring-rose-100"
        onSubmit={(event) => {
          event.preventDefault();
          void onFindCode();
        }}
      >
        <label className="mb-2 block text-sm font-medium" htmlFor="find-code">
          Tìm theo mã · Find by code
        </label>
        <div className="flex gap-2">
          <input
            id="find-code"
            data-testid="find-code"
            value={code}
            onChange={(event) => setCode(event.target.value)}
            placeholder="Nhập mã · e.g. A01"
            autoCapitalize="characters"
            autoCorrect="off"
            spellCheck={false}
            className="h-11 flex-1 rounded-xl bg-[oklch(0.995_0.01_50)] px-3 ring-1 ring-rose-100"
          />
          <button
            type="submit"
            data-testid="find-code-submit"
            disabled={busy}
            className="h-11 rounded-full bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50"
          >
            Tìm
          </button>
        </div>
        {miss ? (
          <p data-testid="find-code-miss" className="mt-2 text-center text-sm text-rose-700">
            Không tìm thấy mã
          </p>
        ) : null}
      </form>
      <label
        data-testid="find-drop"
        className="flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-rose-200 bg-white text-center text-sm text-rose-700"
      >
        {preview ? <FindPreview src={preview} /> : null}
        Thả / chọn ảnh đã lưu để tìm mã
        <input
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void onPhoto(file);
          }}
        />
      </label>
      {matches.map((match) => (
        <div key={match.ma} className="flex items-center justify-between rounded-2xl bg-white px-3 py-2 ring-1 ring-rose-100">
          <p className="font-bold text-rose-800">
            {match.ma}
            <span className="ml-2 text-xs font-medium text-rose-600">{match.color}</span>
          </p>
          <button
            type="button"
            className="inline-flex min-h-11 items-center rounded-full bg-primary px-3 text-xs font-semibold text-primary-foreground"
            onClick={async () => {
              await navigator.clipboard.writeText(match.ma);
              setCopied(match.ma);
            }}
          >
            {copied === match.ma ? "Đã copy mã" : "Copy mã"}
          </button>
        </div>
      ))}
    </div>
  );
}

function StatusChips({
  photos,
  sizes,
  hasPrice,
  needsResearch,
  belowFloor,
}: {
  photos: number;
  sizes: number;
  hasPrice: boolean;
  needsResearch: boolean;
  belowFloor: boolean;
}) {
  const chips: { tone: "warn" | "info" | "ok"; label: string }[] = [];
  if (photos === 0) chips.push({ tone: "warn", label: "Thiếu ảnh" });
  if (sizes === 0) chips.push({ tone: "warn", label: "Thiếu size" });
  if (!hasPrice) chips.push({ tone: "warn", label: "Thiếu giá" });
  if (belowFloor) chips.push({ tone: "warn", label: `Dưới ${Math.round(MARGIN_FLOOR * 100)}%` });
  if (needsResearch) chips.push({ tone: "info", label: "Cần xem tay" });
  if (chips.length === 0) chips.push({ tone: "ok", label: "Đủ để lưu" });
  const toneClass = {
    warn: "bg-[#fbf3e4] text-[#8a5a12]",
    info: "bg-[#e7f1f6] text-[#1f5670]",
    ok: "bg-[#e7f4ec] text-[#246044]",
  };
  return (
    <div className="mb-3 flex flex-wrap gap-1.5" data-testid="intake-status-chips">
      {chips.map((chip) => (
        <span
          key={chip.label}
          className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.08em] ${toneClass[chip.tone]}`}
        >
          {chip.label}
        </span>
      ))}
    </div>
  );
}

function SavedList({
  rows,
  onOpen,
  onCreate,
}: {
  rows: Submission[];
  onOpen: (ma: string) => void;
  onCreate: () => void;
}) {
  return (
    <section className="mt-6" aria-labelledby="saved-list-title">
      <h2 id="saved-list-title" className="text-[21px] leading-tight text-[#3c2a2e]">
        Đã lưu
      </h2>
      <p className="mt-1 text-[12.5px] text-[#7d5360]">Món đã bấm lưu trên máy này.</p>
      {rows.length === 0 ? (
        <div className="mt-3 rounded-2xl bg-white px-4 py-5 ring-1 ring-[#eadfdc]">
          <p className="text-[13.5px] text-[#3c2a2e]">Chưa có món.</p>
          <button
            type="button"
            className="mt-3 inline-flex min-h-11 items-center rounded-full bg-primary px-4 text-sm font-semibold text-primary-foreground"
            onClick={onCreate}
          >
            Thêm món
          </button>
        </div>
      ) : (
        <ul className="mt-3 divide-y divide-[#eadfdc] overflow-hidden rounded-2xl bg-white ring-1 ring-[#eadfdc]">
          {rows.map((row) => {
            const thumb = row.photo_paths?.[0];
            const price = row.sell_usd ? `$${row.sell_usd}` : row.sell_cny ? `¥${row.sell_cny}` : "Thiếu giá";
            return (
              <li key={row.ma}>
                <button
                  type="button"
                  className="flex min-h-11 w-full items-center gap-3 px-3 py-2 text-left hover:bg-[#fbf6f4]"
                  onClick={() => onOpen(row.ma)}
                >
                  {thumb ? (
                    <img src={`/api/photos/${thumb}`} alt="" className="h-12 w-10 rounded-lg object-cover" />
                  ) : (
                    <span className="flex h-12 w-10 items-center justify-center rounded-lg bg-[#f3e6e2] text-[11px] text-[#7d5360]">
                      Ảnh
                    </span>
                  )}
                  <span className="min-w-0 flex-1">
                    <span className="block text-[13.5px] font-semibold tabular text-[#3c2a2e]">{row.ma}</span>
                    <span className="mt-1 flex flex-wrap gap-1">
                      <span className="rounded-full bg-[#f3e6e2] px-2 py-0.5 text-[11px] uppercase tracking-[0.08em] text-[#5c3d48]">
                        {row.kind}
                      </span>
                      {row.size ? (
                        <span className="rounded-full bg-white px-2 py-0.5 text-[11px] uppercase tracking-[0.08em] text-[#7d5360] ring-1 ring-[#eadfdc]">
                          {row.size}
                        </span>
                      ) : (
                        <span className="rounded-full bg-[#fbf3e4] px-2 py-0.5 text-[11px] uppercase tracking-[0.08em] text-[#8a5a12]">
                          Thiếu size
                        </span>
                      )}
                      {row.needs_research ? (
                        <span className="rounded-full bg-[#e7f1f6] px-2 py-0.5 text-[11px] uppercase tracking-[0.08em] text-[#1f5670]">
                          Cần xem tay
                        </span>
                      ) : null}
                    </span>
                  </span>
                  <span className="shrink-0 text-[13.5px] font-semibold tabular text-[#3c2a2e]">{price}</span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
