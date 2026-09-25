"use client";

import { useRef, useState } from "react";
import { Field, FormAlert } from "@/app/admin/fields";
import {
  fetchCatalogExport,
  postAdminImport,
  postAdminSettings,
} from "@/lib/admin-client-save";
import { isOpaqueRscError, opaquePostSaveMessage, publicSaveErrorMessage } from "@/lib/opaque-rsc-error";
import type { SiteRuntimeInfo } from "@/lib/site-runtime";
import { assertImportableHandoffJson } from "@/lib/handoff-json";
import { isCompleteSaveReceipt, saveReceiptLine, silentSaveError } from "@/lib/save-receipt";
import type { Product, SiteSettings } from "@/lib/types";

export function SettingsPanel({
  initial,
  canWrite,
  site,
  onToast,
  onSaved,
}: {
  initial: SiteSettings;
  canWrite: boolean;
  site: SiteRuntimeInfo;
  onToast: (tone: "ok" | "error", text: string) => void;
  onSaved: (products: Product[], settings: SiteSettings) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [lines, setLines] = useState<string[]>(
    initial.announcementLines.length > 0 ? initial.announcementLines : [""],
  );
  const [facebookPageUrl, setFacebookPageUrl] = useState(initial.facebookPageUrl);
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [importMode, setImportMode] = useState<"replace" | "merge">("replace");
  const fileRef = useRef<HTMLInputElement>(null);

  function fail(text: string) {
    setOk(null);
    setError(text);
    onToast("error", text);
  }

  async function save() {
    if (!canWrite) {
      fail("Cannot save settings: storage is not configured.");
      return;
    }
    const cleaned = lines.map((line) => line.trim()).filter(Boolean);
    if (cleaned.length === 0) {
      fail("Add at least one announcement line.");
      return;
    }
    if (!facebookPageUrl.trim()) {
      fail("Messenger URL is required.");
      return;
    }
    setBusy(true);
    try {
      const result = await postAdminSettings({
        announcementLines: cleaned,
        facebookPageUrl,
      });
      if (!result.ok) {
        fail(result.error);
        return;
      }
      if (!isCompleteSaveReceipt(result) || !result.products || !result.settings) {
        fail(silentSaveError());
        return;
      }
      onSaved(result.products, result.settings);
      setLines(result.settings.announcementLines);
      setFacebookPageUrl(result.settings.facebookPageUrl);
      setError(null);
      const line = `Site settings saved · ${saveReceiptLine(result)}.`;
      setOk(line);
      onToast("ok", line);
    } catch (caught) {
      fail(publicSaveErrorMessage(caught, opaquePostSaveMessage()));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h2 className="font-display text-3xl text-ink">Site settings</h2>
        <p className="mt-1 text-sm text-muted">
          Announcement bar and Messenger link. No personal names in copy. Zelle is a method word
          only.
        </p>
      </div>
      {error ? <FormAlert tone="error" text={error} /> : null}
      {ok ? <FormAlert tone="ok" text={ok} /> : null}
      <div className="space-y-3">
        <p className="text-xs uppercase tracking-[0.14em] text-muted">
          Announcement lines · {lines.length}/6
        </p>
        <p className="-mt-1 text-[11px] text-muted">
          Shown in the shop&apos;s top bar, one line at a time. Keep them short.
        </p>
        {lines.map((line, index) => (
          <div key={`line-${index}`} className="flex gap-2">
            <input
              value={line}
              onChange={(event) => {
                const next = lines.slice();
                next[index] = event.target.value;
                setLines(next);
              }}
              placeholder="Facebook livestream"
              className="min-w-0 flex-1 rounded-lg border border-line bg-paper px-3 py-2 text-sm text-ink outline-none focus:border-gold"
            />
            <button
              type="button"
              className="text-xs uppercase tracking-[0.12em] text-muted hover:text-ink"
              onClick={() => {
                const next = lines.filter((_, itemIndex) => itemIndex !== index);
                setLines(next.length > 0 ? next : [""]);
              }}
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          disabled={lines.length >= 6}
          title={lines.length >= 6 ? "Six lines is the max" : "Add another line"}
          className="text-xs uppercase tracking-[0.12em] text-ink hover:text-gold-deep disabled:opacity-40"
          onClick={() => {
            if (lines.length >= 6) {
              return;
            }
            setLines([...lines, ""]);
          }}
        >
          Add line{lines.length >= 6 ? " · max 6" : ""}
        </button>
      </div>
      <Field
        label="Messenger / Facebook Page URL"
        value={facebookPageUrl}
        onChange={setFacebookPageUrl}
        hint="Public Page URL only. Do not put a personal name in the announcement."
      />
      <button
        type="button"
        disabled={busy}
        onClick={() => {
          void save();
        }}
        className="min-h-11 rounded-full bg-ink px-5 py-2.5 text-sm text-paper disabled:opacity-40"
      >
        Save settings{busy ? "…" : ""}
      </button>

      <div className="border-t border-line pt-6">
        <h3 className="font-display text-2xl text-ink">Catalog handoff</h3>
        <p className="mt-1 text-sm text-muted">
          Export catalog.v1 JSON from this {site.mode} site ({site.id}) and import it on the official
          shop. Kit JSON (PR #18) is accepted: letter-or-word types, empty titles keep shop copy,
          OneDrive photo paths are dropped. Replace updates matching mãs and keeps live extras (A03+).
          Merge overlays matching mãs and keeps extras. Does not invent mãs. HTTP: GET
          /api/admin/catalog/export · POST /api/admin/catalog/import. Never intake /api/export.
        </p>
        <fieldset className="mt-4 space-y-1 text-sm text-ink">
          <legend className="text-xs uppercase tracking-[0.14em] text-muted">Import mode</legend>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="import-mode"
              checked={importMode === "replace"}
              onChange={() => setImportMode("replace")}
            />
            Replace live catalog
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="import-mode"
              checked={importMode === "merge"}
              onChange={() => setImportMode("merge")}
            />
            Merge onto live catalog
          </label>
        </fieldset>
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            data-testid="admin-export-catalog"
            data-catalog-export="json"
            disabled={busy}
            onClick={() => {
              void (async () => {
                setBusy(true);
                try {
                  const result = await fetchCatalogExport();
                  if (!result.ok) {
                    fail(result.error);
                    return;
                  }
                  const blob = new Blob([result.json], { type: "application/json" });
                  const href = URL.createObjectURL(blob);
                  const link = document.createElement("a");
                  link.href = href;
                  link.download = result.filename;
                  link.click();
                  URL.revokeObjectURL(href);
                  setError(null);
                  setOk(`Exported ${result.filename}`);
                  onToast("ok", `Exported ${result.filename}`);
                } catch (caught) {
                  fail(isOpaqueRscError(caught) ? opaquePostSaveMessage() : publicSaveErrorMessage(caught, "Export failed."));
                } finally {
                  setBusy(false);
                }
              })();
            }}
            className="min-h-11 rounded-full border border-line px-4 py-2 text-sm text-ink disabled:opacity-40"
          >
            Export catalog.v1
          </button>
          <button
            type="button"
            data-testid="admin-import-catalog"
            disabled={busy || !canWrite}
            onClick={() => fileRef.current?.click()}
            className="min-h-11 rounded-full border border-line px-4 py-2 text-sm text-ink disabled:opacity-40"
          >
            Import catalog.v1
          </button>
          <input
            ref={fileRef}
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              event.target.value = "";
              if (!file) {
                return;
              }
              const confirmed = window.confirm(
                importMode === "merge"
                  ? `Merge ${file.name} onto the live catalog on ${site.id}? Hub ten must stay. Extra mãs (A03+) are kept.`
                  : `Replace the live catalog on ${site.id} with ${file.name}? Hub ten must stay. Extra mãs (A03+) are kept. Shop updates after Blob write + revalidate.`,
              );
              if (!confirmed) {
                return;
              }
              void (async () => {
                setBusy(true);
                try {
                  const text = await file.text();
                  let catalog: unknown;
                  try {
                    catalog = assertImportableHandoffJson(text);
                  } catch (caught) {
                    fail(caught instanceof Error ? caught.message : "Import file is not valid catalog.v1 JSON.");
                    return;
                  }
                  const result = await postAdminImport(catalog, importMode);
                  if (!result.ok) {
                    fail(result.error);
                    return;
                  }
                  if (!isCompleteSaveReceipt(result) || !result.products || !result.settings) {
                    fail(silentSaveError());
                    return;
                  }
                  onSaved(result.products, result.settings);
                  setError(null);
                  const line = `Imported ${result.products.length} mãs · ${saveReceiptLine(result)}.`;
                  setOk(line);
                  onToast("ok", line);
                } catch (caught) {
                  fail(publicSaveErrorMessage(caught, opaquePostSaveMessage()));
                } finally {
                  setBusy(false);
                }
              })();
            }}
          />
        </div>
      </div>
    </div>
  );
}
