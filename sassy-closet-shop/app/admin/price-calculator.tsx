"use client";

import { useMemo, useState } from "react";
import {
  calcPricing,
  deboxForLetter,
  formatUsd2,
  FX_DEFAULT,
  MARGIN_FLOOR,
  marginPct,
  marginVerdict,
} from "@/lib/pricing";
import type { MaLetter } from "@/lib/ma";

function numOrNull(raw: string): number | null {
  const trimmed = raw.trim().replace(/,/g, "");
  if (!trimmed) {
    return null;
  }
  const value = Number(trimmed);
  return Number.isFinite(value) && value >= 0 ? value : null;
}

function strOrEmpty(value: number | null | undefined): string {
  return value === null || value === undefined || !Number.isFinite(value) ? "" : String(value);
}

export function PriceCalculator({
  letter,
  initialCostCny = null,
  initialCostUsd = null,
  initialFx = FX_DEFAULT,
  initialSell = null,
  onApplySell,
  idPrefix = "pc",
}: {
  /** Letter drives the locked V/Q/D debox lookup. Null = unknown letter. */
  letter: MaLetter | null;
  initialCostCny?: number | null;
  initialCostUsd?: number | null;
  initialFx?: number;
  initialSell?: number | null;
  /** When set, an "Apply sell" button fills the draft price. Hidden otherwise. */
  onApplySell?: (sell: number) => void;
  idPrefix?: string;
}) {
  const lockedDebox = letter ? deboxForLetter(letter) : null;
  const [costCny, setCostCny] = useState(() => strOrEmpty(initialCostCny));
  const [costUsd, setCostUsd] = useState(() => strOrEmpty(initialCostUsd));
  const [fx, setFx] = useState(() => strOrEmpty(initialFx));
  const [debox, setDebox] = useState(() => strOrEmpty(lockedDebox));
  const [sellOverride, setSellOverride] = useState(() => strOrEmpty(initialSell));

  const breakdown = useMemo(
    () =>
      calcPricing({
        costCny: numOrNull(costCny),
        costUsd: numOrNull(costUsd),
        fx: numOrNull(fx) ?? 0,
        deboxUsd: numOrNull(debox),
      }),
    [costCny, costUsd, fx, debox],
  );

  const overrideSell = numOrNull(sellOverride);
  const effectiveSell = overrideSell ?? breakdown.sellUsd;
  const verdict = marginVerdict(breakdown.landedUsd, effectiveSell);
  const usingOverride = overrideSell !== null;

  const inputClass =
    "mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold tabular-nums";

  return (
    <div className="rounded-2xl border border-line bg-blush/40 p-4" data-testid="price-calculator">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted">
          Price calculator · sell = ceil(landed ÷ 0.7)
        </p>
        {lockedDebox !== null && letter ? (
          <button
            type="button"
            onClick={() => setDebox(String(lockedDebox))}
            className="text-xs text-gold-deep underline hover:text-ink"
          >
            Reset debox to locked ${lockedDebox.toFixed(2)} ({letter})
          </button>
        ) : null}
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <label className="block text-xs uppercase tracking-[0.12em] text-muted" htmlFor={`${idPrefix}-cny`}>
          Cost ¥ (Taobao)
          <input
            id={`${idPrefix}-cny`}
            inputMode="decimal"
            value={costCny}
            onChange={(event) => setCostCny(event.target.value)}
            placeholder="168"
            className={inputClass}
          />
        </label>
        <label className="block text-xs uppercase tracking-[0.12em] text-muted" htmlFor={`${idPrefix}-usd`}>
          Cost $ (if no ¥)
          <input
            id={`${idPrefix}-usd`}
            inputMode="decimal"
            value={costUsd}
            onChange={(event) => setCostUsd(event.target.value)}
            placeholder="25.00"
            className={inputClass}
          />
        </label>
        <label className="block text-xs uppercase tracking-[0.12em] text-muted" htmlFor={`${idPrefix}-fx`}>
          FX (¥ per $)
          <input
            id={`${idPrefix}-fx`}
            inputMode="decimal"
            value={fx}
            onChange={(event) => setFx(event.target.value)}
            placeholder={String(FX_DEFAULT)}
            className={inputClass}
          />
        </label>
        <label className="block text-xs uppercase tracking-[0.12em] text-muted" htmlFor={`${idPrefix}-debox`}>
          Debox $ (Cainiao share)
          <input
            id={`${idPrefix}-debox`}
            inputMode="decimal"
            value={debox}
            onChange={(event) => setDebox(event.target.value)}
            placeholder={lockedDebox !== null ? lockedDebox.toFixed(2) : "—"}
            className={inputClass}
          />
        </label>
        <label className="block text-xs uppercase tracking-[0.12em] text-muted" htmlFor={`${idPrefix}-sell`}>
          Sell $ override
          <input
            id={`${idPrefix}-sell`}
            inputMode="decimal"
            value={sellOverride}
            onChange={(event) => setSellOverride(event.target.value)}
            placeholder="blank = formula"
            className={inputClass}
          />
        </label>
      </div>
      <p className="mt-1 text-[11px] text-muted">
        {lockedDebox !== null && letter
          ? `Debox locked $${lockedDebox.toFixed(2)} for ${letter} (V/Q/D table).`
          : "Letter has no locked debox — enter the Cainiao share or leave blank. Never invent one."}{" "}
        ¥ cost wins over $ cost when both are set.
      </p>

      <dl className="mt-3 space-y-1 text-sm tabular-nums" aria-live="polite">
        <div className="flex justify-between gap-4">
          <dt className="text-muted">Cost</dt>
          <dd className="text-ink">
            {numOrNull(costCny) !== null && numOrNull(fx) ? (
              <>¥{numOrNull(costCny)} ÷ {numOrNull(fx)} = {formatUsd2(breakdown.costUsd)}</>
            ) : (
              <>{formatUsd2(breakdown.costUsd)} (USD cost)</>
            )}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-muted">Landed</dt>
          <dd className="text-ink">
            {formatUsd2(breakdown.costUsd)} + {formatUsd2(numOrNull(debox))} debox ={" "}
            <strong>{formatUsd2(breakdown.landedUsd)}</strong>
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-muted">Sell {usingOverride ? "(override)" : "(formula)"}</dt>
          <dd className="text-ink">
            {usingOverride ? (
              <strong>{formatUsd2(effectiveSell)}</strong>
            ) : (
              <>ceil({formatUsd2(breakdown.landedUsd)} ÷ 0.7) = <strong>{formatUsd2(effectiveSell)}</strong></>
            )}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-muted">Margin at sell</dt>
          <dd className="text-ink">
            {breakdown.landedUsd !== null && effectiveSell !== null
              ? `${(marginPct(breakdown.landedUsd, effectiveSell) * 100).toFixed(1)}%`
              : "—"}
          </dd>
        </div>
      </dl>

      <div className="mt-3 flex flex-wrap items-center gap-3">
        {verdict === "ok" ? (
          <p className="rounded-xl border border-line bg-paper px-3 py-2 text-sm text-ink" data-testid="price-verdict-ok">
            ✓ At/above the {Math.round(MARGIN_FLOOR * 100)}% floor — safe to price {formatUsd2(effectiveSell)}.
          </p>
        ) : (
          <p
            className="rounded-xl border border-gold-deep/40 bg-paper px-3 py-2 text-sm text-gold-deep"
            data-testid="price-verdict-inbox"
          >
            ⚠ Inbox giá — {effectiveSell === null ? "sell is blank" : `under the ${Math.round(MARGIN_FLOOR * 100)}% margin floor`}.
            Caption stays “Inbox giá”.
          </p>
        )}
        {onApplySell && verdict === "ok" && effectiveSell !== null ? (
          <button
            type="button"
            onClick={() => onApplySell(effectiveSell)}
            className="min-h-10 rounded-full bg-ink px-4 py-2 text-xs uppercase tracking-[0.12em] text-paper"
          >
            Apply {formatUsd2(effectiveSell)} to draft
          </button>
        ) : null}
      </div>
    </div>
  );
}
