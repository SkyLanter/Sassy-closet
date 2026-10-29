/**
 * Sassy Closet auto-price calculator.
 *
 * Pipeline rule (Boss-defined):
 *   landed = CNY cost / FX + letter debox
 *   sell   = ceil(landed / 0.75)         // 25% gross margin
 *   if sell < $10, sell = sell + $2
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
import { normalizeMa } from "./mint";

/** Target gross margin baked into the auto price (25%). */
export const TARGET_MARGIN = 0.25;

/** Sell divisor: 1 - 25% = 0.75. */
export const MARGIN_DIVISOR = 1 - TARGET_MARGIN;

/** Boss rule: if ceil(landed / 0.75) is under $10, add $2. */
export const UNDER_TEN_LIMIT_USD = 10;
export const UNDER_TEN_BUMP_USD = 2;

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
  /** Suggested sell price in USD: ceil(landed / 0.75) at 25% margin, +$2 under $10. */
  sellUsd: number;
  /** USD margin (sell - landed). */
  marginUsd: number;
  /** Margin as a fraction of sell (0.25-ish before rounding, ceil bumps it up). */
  marginPct: number;
  /** Whether this price clears the 35% caption floor. */
  captionEligible: boolean;
};

const TIER_LOW_SELL = 25;
const TIER_HIGH_SELL = 45;
const TIER_LOW_MARGIN = 0.35;
const TIER_HIGH_MARGIN = 0.25;
const S06_LOCK_USD = 25;

function ceilQuote(value: number): number {
  const scaled = Math.round(value * 1e8) / 1e8;
  return Math.ceil(scaled - 1e-9);
}

/** Margin for a whole-dollar sell. Same bands as auto-list. */
export function tieredMarginForSell(sell: number): number {
  if (sell <= TIER_LOW_SELL) return TIER_LOW_MARGIN;
  if (sell >= TIER_HIGH_SELL) return TIER_HIGH_MARGIN;
  const span = TIER_HIGH_SELL - TIER_LOW_SELL;
  return TIER_LOW_MARGIN + (TIER_HIGH_MARGIN - TIER_LOW_MARGIN) * ((sell - TIER_LOW_SELL) / span);
}

function quoteFromLanded(landedUsd: number, sellForMargin: number): number {
  const divisor = 1 - tieredMarginForSell(sellForMargin);
  const quoted = ceilQuote(landedUsd / divisor);
  if (quoted < UNDER_TEN_LIMIT_USD) return quoted + UNDER_TEN_BUMP_USD;
  return quoted;
}

/**
 * Smallest whole-dollar sell that does not undercut the tiered margin.
 * Same fixed point as scripts/autolist.py price().
 */
export function tieredSellUsd(landedUsd: number): number | null {
  if (!Number.isFinite(landedUsd) || landedUsd <= 0) return null;
  const ceiling = quoteFromLanded(landedUsd, 1) + UNDER_TEN_BUMP_USD;
  for (let sell = 1; sell <= ceiling; sell += 1) {
    if (sell >= quoteFromLanded(landedUsd, sell)) return sell;
  }
  return null;
}

export function sellUsdFromLanded(landedUsd: number): number {
  const quoted = Math.ceil(landedUsd / MARGIN_DIVISOR);
  if (quoted < UNDER_TEN_LIMIT_USD) {
    return quoted + UNDER_TEN_BUMP_USD;
  }
  return quoted;
}

export function computeAutoPrice(input: PriceInputs): PriceBreakdown | null {
  const { costCny, fxRate, kind, deboxOverrides } = input;
  if (!Number.isFinite(costCny) || costCny <= 0) return null;
  if (!Number.isFinite(fxRate) || fxRate <= 0) return null;
  const deboxUsd = deboxFor(kind, deboxOverrides);
  const landedUsd = costCny / fxRate + deboxUsd;
  const sellUsd = sellUsdFromLanded(landedUsd);
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

export type SellPriceInput = {
  sellUsd: string;
  sellCny: string;
  sellCurrency: string;
  costCny: string;
  costUsd: string;
  costCurrency: string;
  kind: string;
  fxRate: number;
  deboxOverrides?: DeboxOverrides;
};

/**
 * Blank sell is calculated later. A typed sell is flagged only when cost is
 * known and the margin is under the caption floor. Unknown cost does not block.
 */
export type SellPriceFlag = "later" | "under-margin" | "ok";

export type IntakePriceView = {
  label: string;
  dollars: number | null;
  flag: SellPriceFlag;
};

function positiveAmount(raw: string): number | null {
  const value = Number(String(raw).trim());
  if (!Number.isFinite(value) || value <= 0) return null;
  return value;
}

/** Goods cost in USD plus the letter debox. CNY is converted with the weekly FX. */
export function landedUsdFromCosts(input: {
  kind: string;
  costCny: string;
  costUsd: string;
  costCurrency: string;
  fxRate: number;
  deboxOverrides?: DeboxOverrides;
}): number | null {
  const fx = input.fxRate;
  if (!Number.isFinite(fx) || fx <= 0) return null;
  const cny = positiveAmount(input.costCny);
  const usd = positiveAmount(input.costUsd);
  const currency = input.costCurrency.trim().toUpperCase();
  let goodsUsd: number | null = null;
  if (currency === "CNY" && cny) goodsUsd = cny / fx;
  else if (usd) goodsUsd = usd;
  else if (cny) goodsUsd = cny / fx;
  if (goodsUsd == null) return null;
  const landed = goodsUsd + deboxFor(input.kind, input.deboxOverrides);
  return landed > 0 ? landed : null;
}

function storedSellUsd(input: SellPriceInput): number | null {
  const currency = input.sellCurrency.trim().toUpperCase();
  if (currency === "CNY") {
    const cny = positiveAmount(input.sellCny);
    if (!cny || !Number.isFinite(input.fxRate) || input.fxRate <= 0) return null;
    return cny / input.fxRate;
  }
  return positiveAmount(input.sellUsd);
}

function underTieredMargin(sellUsd: number, landed: number | null, quote: number | null): boolean {
  if (landed == null || quote == null || !(sellUsd > 0)) return false;
  if (sellUsd + 1e-6 < quote) return true;
  return (sellUsd - landed) / sellUsd < MARGIN_FLOOR;
}

/**
 * What the intake list should show. A blank sell with enough cost becomes the
 * tiered dollar. "Tính giá sau" is only when that dollar cannot be computed.
 * S06 is always $25. A price under the margin is flagged and still shown.
 */
export function intakePriceView(input: SellPriceInput & { ma: string }): IntakePriceView {
  if (normalizeMa(input.ma) === "S06") {
    return { label: `$${S06_LOCK_USD}`, dollars: S06_LOCK_USD, flag: "ok" };
  }
  const landed = landedUsdFromCosts(input);
  const quote = landed == null ? null : tieredSellUsd(landed);
  const stored = storedSellUsd(input);
  if (stored != null) {
    const currency = input.sellCurrency.trim().toUpperCase();
    const label = currency === "CNY" && input.sellCny.trim() ? `¥${input.sellCny.trim()}` : `$${input.sellUsd.trim()}`;
    return {
      label,
      dollars: stored,
      flag: underTieredMargin(stored, landed, quote) ? "under-margin" : "ok",
    };
  }
  if (quote != null && landed != null) {
    return {
      label: `$${quote}`,
      dollars: quote,
      flag: underTieredMargin(quote, landed, quote) ? "under-margin" : "ok",
    };
  }
  return { label: "Tính giá sau", dollars: null, flag: "later" };
}

export function sellPriceFlag(input: SellPriceInput): SellPriceFlag {
  const currency = input.sellCurrency.toUpperCase();
  const sellBlank = currency === "CNY" ? !input.sellCny.trim() : !input.sellUsd.trim();
  if (sellBlank) return "later";

  const costCnyNum = Number(String(input.costCny).trim());
  const costUsdNum = Number(String(input.costUsd).trim());
  const costKnown =
    input.costCurrency.toUpperCase() === "CNY"
      ? Number.isFinite(costCnyNum) && costCnyNum > 0
      : Number.isFinite(costUsdNum) && costUsdNum > 0;
  if (!costKnown) return "ok";

  const costCnyValue =
    input.costCurrency.toUpperCase() === "CNY" ? costCnyNum : costUsdNum * input.fxRate;
  const breakdown = computeAutoPrice({
    costCny: costCnyValue,
    fxRate: input.fxRate,
    kind: input.kind,
    deboxOverrides: input.deboxOverrides,
  });
  if (!breakdown) return "ok";
  const sellNum = currency === "CNY" ? Number(input.sellCny) / input.fxRate : Number(input.sellUsd);
  if (!Number.isFinite(sellNum) || sellNum <= 0) return "ok";
  const marginPct = (sellNum - breakdown.landedUsd) / sellNum;
  if (marginPct < MARGIN_FLOOR) return "under-margin";
  return "ok";
}

/**
 * Caption price line for a submission.
 * - sell blank            -> "Inbox giá"
 * - margin < 35% (known)  -> "Inbox giá"
 * - otherwise             -> the sell price as before ("$X" / "¥Y")
 */
export function captionPriceLine(input: SellPriceInput): string {
  if (sellPriceFlag(input) !== "ok") return "Inbox giá";
  const currency = input.sellCurrency.toUpperCase();
  if (currency === "CNY" && input.sellCny) return `¥${input.sellCny}`;
  if (input.sellUsd) return `$${input.sellUsd}`;
  if (input.sellCny) return `¥${input.sellCny}`;
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
