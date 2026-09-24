"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { MaMark } from "@/components/ma-mark";
import { fetchIntakeStagedAction, setPipelineStageAction } from "@/app/admin/actions";
import { FormAlert } from "@/app/admin/fields";
import { PriceCalculator } from "@/app/admin/price-calculator";
import {
  intakeToPrefill,
  parseIntakeImportJson,
  type IntakePrefill,
  type IntakeSubmission,
} from "@/lib/intake-import";
import { writeIntakePrefill } from "@/lib/intake-prefill";
import { MA_LETTERS, type MaLetter } from "@/lib/ma";
import type { PipelineStageId } from "@/lib/pipeline";
import type { Product } from "@/lib/types";

type ToastFn = (tone: "ok" | "error", text: string) => void;

function truthDot(truth: "confirmed" | "unconfirmed"): string {
  return truth === "confirmed" ? "bg-emerald-600" : "bg-red-500";
}

function truthLabel(truth: "confirmed" | "unconfirmed"): string {
  return truth === "confirmed" ? "confirmed" : "unconfirmed";
}

function letterOrNull(letter: string): MaLetter | null {
  return (MA_LETTERS as readonly string[]).includes(letter) ? (letter as MaLetter) : null;
}

export function IntakeImportPanel({
  products,
  canWrite,
  onToast,
}: {
  products: Product[];
  canWrite: boolean;
  onToast: ToastFn;
}) {
  const router = useRouter();
  const [items, setItems] = useState<IntakeSubmission[]>([]);
  const [source, setSource] = useState<"fetch" | "paste" | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paste, setPaste] = useState("");
  const [selectedMa, setSelectedMa] = useState<string | null>(null);
  const [suggestedSell, setSuggestedSell] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  const selected = useMemo(
    () => items.find((item) => item.ma === selectedMa) ?? null,
    [items, selectedMa],
  );
  const prefill: IntakePrefill | null = useMemo(
    () => (selected ? intakeToPrefill(selected) : null),
    [selected],
  );
  const alreadyInCatalog = prefill ? products.some((product) => product.ma === prefill.intakeMa) : false;

  function select(ma: string) {
    setSelectedMa(ma);
    setSuggestedSell(null);
    setError(null);
  }

  async function fetchStaged() {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchIntakeStagedAction();
      if (!result.ok) {
        setError(result.error);
        return;
      }
      setItems(result.items);
      setSource("fetch");
      setSelectedMa(result.items[0]?.ma ?? null);
      setSuggestedSell(null);
      if (result.items.length === 0) {
        onToast("ok", "Intake site answered — no staged submissions right now.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Fetch failed.");
    } finally {
      setLoading(false);
    }
  }

  function importPaste() {
    setError(null);
    const result = parseIntakeImportJson(paste);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    setItems(result.submissions);
    setSource("paste");
    setSelectedMa(result.submissions[0]?.ma ?? null);
    setSuggestedSell(null);
    onToast("ok", `Parsed ${result.submissions.length} staged submission${result.submissions.length === 1 ? "" : "s"}.`);
  }

  async function markStage(ma: string, stage: PipelineStageId): Promise<boolean> {
    if (!canWrite) {
      onToast("error", "Pipeline tracker needs a writable store (Blob/KV/local).");
      return false;
    }
    const result = await setPipelineStageAction(ma, stage, true);
    if (!result.ok) {
      onToast("error", result.error);
      return false;
    }
    return true;
  }

  async function applySell(sell: number) {
    if (!prefill) {
      return;
    }
    setSuggestedSell(sell);
    const ok = await markStage(prefill.intakeMa, "priced");
    onToast(ok ? "ok" : "error", ok ? `Priced ${prefill.intakeMa} at $${sell} — saved to the draft.` : "Price kept, tracker not saved.");
  }

  async function createDraft() {
    if (!prefill || busy) {
      return;
    }
    setBusy(true);
    try {
      writeIntakePrefill({ ...prefill, suggestedSell });
      const ok = await markStage(prefill.intakeMa, "intake");
      onToast(
        ok ? "ok" : "error",
        ok
          ? `Draft staged from intake ${prefill.intakeMa} — status hold, never available.`
          : "Draft staged, but the tracker did not save.",
      );
      router.push("/admin/new");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-3xl text-ink">Intake import</h2>
        <p className="mt-1 max-w-2xl text-sm text-muted">
          Pull staged intake submissions into draft products. Drafts are staged only — status hold,
          never available, never touching Square. The intake app keeps its own store; this page
          fetches its staged rows over /api/submissions, or takes a pasted submission JSON.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => void fetchStaged()}
          disabled={loading}
          className="min-h-11 rounded-full bg-ink px-5 py-2.5 text-sm text-paper disabled:opacity-40"
        >
          {loading ? "Fetching…" : "Fetch staged from intake site"}
        </button>
      </div>

      <div className="rounded-2xl border border-line p-4">
        <label className="block text-xs uppercase tracking-[0.14em] text-muted" htmlFor="intake-paste">
          Or paste submission JSON
          <textarea
            id="intake-paste"
            value={paste}
            onChange={(event) => setPaste(event.target.value)}
            placeholder='Paste one submission object, or the {"submissions": [...]} payload from the intake /api/submissions'
            rows={4}
            className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 font-mono text-xs normal-case tracking-normal text-ink outline-none focus:border-gold"
          />
        </label>
        <button
          type="button"
          onClick={importPaste}
          disabled={!paste.trim()}
          className="mt-2 min-h-10 rounded-full border border-line px-4 py-2 text-xs uppercase tracking-[0.12em] text-ink disabled:opacity-40"
        >
          Parse paste
        </button>
      </div>

      {error ? <FormAlert tone="error" text={error} /> : null}

      {items.length > 0 ? (
        <div className="rounded-2xl border border-line">
          <p className="border-b border-line px-4 py-3 text-xs uppercase tracking-[0.14em] text-muted">
            {items.length} staged submission{items.length === 1 ? "" : "s"} · via {source === "fetch" ? "intake site" : "paste"}
          </p>
          <ul className="divide-y divide-line">
            {items.map((item) => (
              <li key={item.ma}>
                <button
                  type="button"
                  onClick={() => select(item.ma)}
                  className={`flex w-full flex-wrap items-center gap-3 px-4 py-3 text-left hover:bg-blush/40 ${item.ma === selectedMa ? "bg-blush/60" : ""}`}
                >
                  <MaMark ma={item.ma} className="text-[13px] tracking-[0.12em]" />
                  <span className="text-sm text-ink">{item.color || <span className="text-muted">no color yet</span>}</span>
                  <span className="text-xs text-muted">{item.size || "no sizes"}</span>
                  <span className="text-xs tabular-nums text-muted">
                    {item.photo_paths.length} photo{item.photo_paths.length === 1 ? "" : "s"}
                  </span>
                  <span className="ml-auto text-xs text-muted">
                    {item.updated_at ? item.updated_at.slice(0, 10) : ""}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : source ? (
        <p className="rounded-2xl border border-dashed border-line px-4 py-10 text-center text-sm text-muted">
          No staged submissions found.
        </p>
      ) : null}

      {prefill && selected ? (
        <div className="space-y-4 rounded-2xl border border-line p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h3 className="font-display text-2xl text-ink">
              <MaMark ma={prefill.intakeMa} className="tracking-[0.06em]" />
            </h3>
            <button
              type="button"
              onClick={() => void createDraft()}
              disabled={busy}
              className="min-h-11 rounded-full bg-ink px-5 py-2.5 text-sm text-paper disabled:opacity-40"
            >
              {busy ? "Staging…" : "Create draft →"}
            </button>
          </div>

          {alreadyInCatalog ? (
            <FormAlert
              tone="error"
              text={`${prefill.intakeMa} is already in the catalog. Importing would duplicate it — open Edit instead, unless this is a re-shoot.`}
            />
          ) : null}

          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-muted">
              Colors · <span className="inline-block h-2.5 w-2.5 rounded-full bg-emerald-600 align-middle" /> confirmed ·{" "}
              <span className="inline-block h-2.5 w-2.5 rounded-full bg-red-500 align-middle" /> unconfirmed
            </p>
            {prefill.colors.length === 0 ? (
              <p className="mt-1 text-sm text-muted">No colors — stays empty until research.</p>
            ) : (
              <ul className="mt-2 space-y-1.5">
                {prefill.colors.map((color) => (
                  <li key={color.name} className="flex items-center gap-2 text-sm">
                    <span className={`inline-block h-3 w-3 shrink-0 rounded-full ${truthDot(color.truth)}`} aria-hidden />
                    <span className="text-ink">{color.name}</span>
                    <span className="text-xs text-muted">
                      {truthLabel(color.truth)} · {color.source}
                      {color.note ? ` · ${color.note}` : ""}
                    </span>
                  </li>
                ))}
              </ul>
            )}
            <p className="mt-1 text-[11px] text-muted">
              Hexes are never invented — pick a swatch per color on the draft before Save (Save refuses blank hexes).
            </p>
          </div>

          <div className="grid gap-3 text-sm sm:grid-cols-2">
            <p>
              <span className="text-xs uppercase tracking-[0.14em] text-muted">Sizes </span>
              <span className="text-ink">{prefill.sizes.length > 0 ? prefill.sizes.join(" ") : "—"}</span>
            </p>
            <p>
              <span className="text-xs uppercase tracking-[0.14em] text-muted">Photos </span>
              <span className="text-ink">
                {prefill.photoCount} staged
                {prefill.photoLink ? (
                  <span className="text-muted"> · OneDrive {prefill.photoLink}</span>
                ) : null}
              </span>
            </p>
            <p className="sm:col-span-2">
              <span className="text-xs uppercase tracking-[0.14em] text-muted">Taobao </span>
              {prefill.sourceLink ? (
                <a href={prefill.sourceLink} target="_blank" rel="noreferrer" className="text-gold-deep underline break-all">
                  {prefill.sourceLink}
                </a>
              ) : (
                <span className="text-muted">no link — never invent one</span>
              )}
            </p>
            {prefill.blurb ? (
              <p className="sm:col-span-2">
                <span className="text-xs uppercase tracking-[0.14em] text-muted">Blurb </span>
                <span className="text-ink">{prefill.blurb}</span>
              </p>
            ) : null}
          </div>

          {prefill.warnings.length > 0 ? (
            <ul className="space-y-1 rounded-xl border border-gold-deep/40 bg-blush px-4 py-3 text-sm text-gold-deep">
              {prefill.warnings.map((warning) => (
                <li key={warning}>⚠ {warning}</li>
              ))}
            </ul>
          ) : null}

          {prefill.autoPrice ? (
            <div className="rounded-xl border border-line bg-blush/40 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.14em] text-muted">Intake auto-price</p>
              <p className="mt-1 text-sm text-ink">
                <span className="text-lg font-semibold tabular-nums">${prefill.autoPrice.sellUsd}</span>
                <span className="text-muted">
                  {" "}· landed ${prefill.autoPrice.landedUsd.toFixed(2)} (debox $
                  {prefill.autoPrice.deboxUsd.toFixed(2)}) · margin{" "}
                  {(prefill.autoPrice.marginPct * 100).toFixed(0)}%
                </span>
              </p>
              <button
                type="button"
                onClick={() => {
                  const sell = prefill.autoPrice?.sellUsd;
                  if (sell != null) {
                    void applySell(sell);
                  }
                }}
                className="mt-2 min-h-10 rounded-full border border-line bg-paper px-4 py-2 text-xs uppercase tracking-[0.12em] text-ink"
              >
                Use ${prefill.autoPrice.sellUsd} as suggested sell
              </button>
            </div>
          ) : null}

          {prefill.taobaoSnapshot ? (
            <p className="text-xs text-muted">
              Taobao snapshot at intake: {prefill.taobaoSnapshot.title}
              {prefill.taobaoSnapshot.listCny ? ` · list ¥${prefill.taobaoSnapshot.listCny}` : ""}
              {prefill.taobaoSnapshot.promoCny ? ` · promo ¥${prefill.taobaoSnapshot.promoCny}` : ""} ·{" "}
              {prefill.taobaoSnapshot.colors.length} seller color
              {prefill.taobaoSnapshot.colors.length === 1 ? "" : "s"}
            </p>
          ) : null}

          <PriceCalculator
            letter={letterOrNull(prefill.letter)}
            initialCostCny={prefill.costCny}
            initialCostUsd={prefill.costUsd}
            initialSell={suggestedSell}
            onApplySell={(sell) => void applySell(sell)}
            idPrefix={`intake-${prefill.intakeMa}`}
          />
          {suggestedSell !== null ? (
            <p className="text-sm text-ink" data-testid="intake-suggested-sell">
              Suggested sell ${suggestedSell} travels with the draft to Add.
            </p>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
