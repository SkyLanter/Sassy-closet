/**
 * Sassy Closet auto-price calculator.
 *
 * Pipeline rule (Boss-defined):
 *   landed = CNY cost / FX + letter debox
 *   sell   = ceil(landed / 0.7)          // 30% gross margin
 *   margin$ = sell - landed
 *   margin% = margin$ / sell
 *
 * Debox table: V/Q/D = $7.50 (LOCKED — can never be overridden).
 * Other letters default to $0 unless Boss sets a per-letter value.
 *
 * Caption guard: if the sell price is blank, or its margin lands under
 * the 35% floor, the price caption stays "Inbox giá".
 */
import type { KindCode } from "./kinds";

/** Target gross margin baked into the auto price (30%). */
export const TARGET_MARGIN = 0.3;

/** Caption margin floor: below this the price line stays "Inbox giá". */
export const MARGIN_FLOOR = 0.35;

/** Debox fee locked for V/Q/D — overrides are ignored for these letters. */
export const DEBOX_LOCKED: Record<string, number> = {
  V: 7.5,
  Q: 7.5,
  D: 7.5,
};

/** Default FX (1 USD = 6.723 CNY) — the store rate, settable in the UI. */
export const DEFAULT_FX = 6.723;

/** Per-letter debox overrides for letters other than V/Q/D (USD). */
export type DeboxOverrides = Partial<Record<KindCode, number>>;

export function deboxFor(kind: string, overrides?: DeboxOverrides): number {
  const upper = kind.toUpperCase();
  if (upper in DEBOX_LOCKED) return DEBOX_LOCKED[upper];
  const override = overrides?.[upper as KindCode];
  if (typeof override === "number" && Number.isFinite(override) && override >= 0) {
    return override;
  }
  return 0;
}

export type PriceInputs = {
  costCny: number;
  fxRate: number;
  kind: string;
  deboxOverrides?: DeboxOverrides;
};

export type PriceBreakdown = {  /** Landed cost in USD: CNY/FX + debox. */
  landedUsd: number;
  deboxUsd: number;
  /** Suggested sell price in USD: ceil(landed / 0.7) at 30% margin. */
  sellUsd: number;
  /** USD margin (sell - landed). */
  marginUsd: number;
  /** Margin as a fraction of sell (0.3-ish before rounding, ceil bumps it up). */
  marginPct: number;
  /** Whether this price clears the 35% caption floor. */
  captionEligible: boolean;
};

export function computeAutoPrice(input: PriceInputs): PriceBreakdown | null {
  const { costCny, fxRate, kind, deboxOverrides } = input;
  if (!Number.isFinite(costCny) || costCny <= 0) return null;
  if (!Number.isFinite(fxRate) || fxRate <= 0) return null;
  const deboxUsd = deboxFor(kind, deboxOverrides);
  const landedUsd = costCny / fxRate + deboxUsd;
  const sellUsd = Math.ceil(landedUsd / (1 - TARGET_MARGIN));
  const marginUsd = sellUsd - landedUsd;
  const marginPct = sellUsd > 0 ? marginUsd / sellUsd : 0;
  return {
    landedUsd,
    deboxUsd,
    sellUsd,
    marginUsd,
    marginPct,
    captionEligible: marginPct >= MARGIN_FLOOR,
  };
}

/**
 * Caption price line for a submission.
 * - sell blank            -> "Inbox giá"
 * - margin < 35% (known)  -> "Inbox giá"
 * - otherwise             -> the sell price as before ("$X" / "¥Y")
 */
export function captionPriceLine(input: {
  sellUsd: string;
  sellCny: string;
  sellCurrency: string;
  costCny: string;
  costUsd: string;
  costCurrency: string;
  kind: string;
  fxRate: number;
  deboxOverrides?: DeboxOverrides;
}): string {
  const { sellUsd, sellCny, sellCurrency } = input;
  const currency = sellCurrency.toUpperCase();
  const sellBlank = currency === "CNY" ? !sellCny.trim() : !sellUsd.trim();
  if (sellBlank) return "Inbox giá";

  // Margin guard: only when the cost side is known.
  const costCnyNum = Number(String(input.costCny).trim());
  const costUsdNum = Number(String(input.costUsd).trim());
  const costKnown =
    input.costCurrency.toUpperCase() === "CNY"
      ? Number.isFinite(costCnyNum) && costCnyNum > 0
      : Number.isFinite(costUsdNum) && costUsdNum > 0;
  if (costKnown) {
    const costCnyValue =
      input.costCurrency.toUpperCase() === "CNY" ? costCnyNum : costUsdNum * input.fxRate;
    const breakdown = computeAutoPrice({
      costCny: costCnyValue,
      fxRate: input.fxRate,
      kind: input.kind,
      deboxOverrides: input.deboxOverrides,
    });
    if (breakdown) {
      const sellNum = currency === "CNY" ? Number(sellCny) / input.fxRate : Number(sellUsd);
      if (Number.isFinite(sellNum) && sellNum > 0) {
        const marginPct = (sellNum - breakdown.landedUsd) / sellNum;
        if (marginPct < MARGIN_FLOOR) return "Inbox giá";
      }
    }
  }

  if (currency === "CNY" && sellCny) return `¥${sellCny}`;
  if (sellUsd) return `$${sellUsd}`;
  if (sellCny) return `¥${sellCny}`;
  return "Inbox giá";
}

/** Type guard for PriceBreakdown parsed from a client payload. */
export function isPriceBreakdown(value: unknown): value is PriceBreakdown {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.landedUsd === "number" &&
    typeof v.deboxUsd === "number" &&
    typeof v.sellUsd === "number" &&
    typeof v.marginUsd === "number" &&
    typeof v.marginPct === "number"
  );
}
