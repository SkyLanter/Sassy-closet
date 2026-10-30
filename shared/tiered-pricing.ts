/**
 * Tiered sell quote shared by the intake app and the shop.
 *
 * Same rule as scripts/autolist.py. Live flat 25% calculators stay in
 * each app's lib/pricing.ts. This module does not read or write a catalog.
 *
 * m = 0.35 when the resulting sell is <= $25.
 * m = 0.25 when the resulting sell is >= $45.
 * Between those, m moves in a straight line.
 * sell = ceil(landed / (1 - m)).
 * When that ceil is under $10, add $2.
 * The quote is the smallest whole dollar that does not undercut that sell.
 * wouldBeLiveUsd keeps S06 at $25.
 */

export const TIERED_LOW_SELL = 25;
export const TIERED_HIGH_SELL = 45;
export const TIERED_LOW_MARGIN = "0.35";
export const TIERED_HIGH_MARGIN = "0.25";
export const UNDER_TEN_LIMIT_USD = 10;
export const UNDER_TEN_BUMP_USD = 2;
export const S06_LOCK_USD = 25;
/** Store rate shared with the live calculators: 1 USD = 6.723 CNY. */
export const FX_CNY_PER_USD = "6.723";

const Z = BigInt(0);
const ONE = BigInt(1);
const TEN = BigInt(10);
const FX = { n: BigInt(6723), d: BigInt(1000) };
const DEBOX_750 = { n: BigInt(15), d: BigInt(2) };
const ZERO = { n: Z, d: ONE };

export type WouldBeReason = "locked" | "no-cost" | "tiered";

export type IntakePriceInput = {
  ma: string;
  kind: string;
  liveUsd: number;
  costCny: string | null;
  costUsd: string | null;
};

export type WouldBePrice = {
  ma: string;
  liveUsd: number;
  wouldBeUsd: number;
  applied: boolean;
  reason: WouldBeReason;
};

type Frac = { n: bigint; d: bigint };

function gcd(a: bigint, b: bigint): bigint {
  let x = a < Z ? -a : a;
  let y = b < Z ? -b : b;
  while (y !== Z) {
    const next = x % y;
    x = y;
    y = next;
  }
  return x;
}

function frac(n: bigint, d: bigint): Frac {
  if (d === Z) {
    throw new Error("zero denominator");
  }
  if (d < Z) {
    n = -n;
    d = -d;
  }
  const divisor = gcd(n, d);
  return { n: n / divisor, d: d / divisor };
}

function add(left: Frac, right: Frac): Frac {
  return frac(left.n * right.d + right.n * left.d, left.d * right.d);
}

function div(left: Frac, right: Frac): Frac {
  if (right.n === Z) {
    throw new Error("division by zero");
  }
  return frac(left.n * right.d, left.d * right.n);
}

function parsePositiveDecimal(raw: string | null): Frac | null {
  if (raw == null) return null;
  const text = raw.trim();
  if (!/^\d+(?:\.\d+)?$/.test(text)) return null;
  const [whole, fraction = ""] = text.split(".");
  const scale = TEN ** BigInt(fraction.length);
  const digits = fraction === "" ? "0" : fraction;
  const n = BigInt(whole) * scale + BigInt(digits);
  if (n <= Z) return null;
  return frac(n, scale);
}

function kindLetter(kind: string, ma: string): string {
  const fromKind = kind.trim().toUpperCase();
  if (fromKind.length > 0) return fromKind.charAt(0);
  return ma.trim().toUpperCase().charAt(0);
}

/** Locked Cainiao share. Every other letter is $0. Overrides are not applied. */
export function lockedDeboxUsd(kind: string): "7.50" | "0" {
  const letter = kind.trim().toUpperCase().charAt(0);
  if (letter === "V" || letter === "Q" || letter === "D") return "7.50";
  return "0";
}

function deboxFrac(kind: string, ma: string): Frac {
  return lockedDeboxUsd(kindLetter(kind, ma)) === "7.50" ? DEBOX_750 : ZERO;
}

function landedFromCost(input: IntakePriceInput): Frac | null {
  const debox = deboxFrac(input.kind, input.ma);
  const cny = parsePositiveDecimal(input.costCny);
  if (cny) return add(div(cny, FX), debox);
  const usd = parsePositiveDecimal(input.costUsd);
  if (usd) return add(usd, debox);
  return null;
}

function toSafeInt(value: bigint): number {
  if (value > BigInt(Number.MAX_SAFE_INTEGER)) {
    throw new Error("sell quote is too large");
  }
  return Number(value);
}

function ceilDiv(landed: Frac, divisor: Frac): bigint {
  const numerator = landed.n * divisor.d;
  const denominator = landed.d * divisor.n;
  return (numerator + denominator - ONE) / denominator;
}

function divisorForSell(sell: number): Frac {
  if (sell <= TIERED_LOW_SELL) return frac(BigInt(65), BigInt(100));
  if (sell >= TIERED_HIGH_SELL) return frac(BigInt(75), BigInt(100));
  return frac(BigInt(sell + 105), BigInt(200));
}

function formatFrac(value: Frac): string {
  const whole = value.n / value.d;
  let remainder = value.n % value.d;
  if (remainder === Z) return whole.toString();
  let digits = "";
  for (let place = 0; place < 8 && remainder !== Z; place += 1) {
    remainder *= TEN;
    digits += (remainder / value.d).toString();
    remainder %= value.d;
  }
  return `${whole}.${digits}`.replace(/0+$/, "");
}

/** Margin used for a candidate whole-dollar sell. Exact decimal, not a float. */
export function marginForSell(sell: number): string {
  if (!Number.isInteger(sell)) {
    throw new Error("margin sell must be a whole dollar");
  }
  if (sell <= TIERED_LOW_SELL) return TIERED_LOW_MARGIN;
  if (sell >= TIERED_HIGH_SELL) return TIERED_HIGH_MARGIN;
  return formatFrac(frac(BigInt(95 - sell), BigInt(200)));
}

function quoteFromLanded(landed: Frac, sellForMargin: number): number {
  if (!Number.isInteger(sellForMargin) || sellForMargin < 1) {
    throw new Error("margin sell must be a positive whole dollar");
  }
  const quoted = toSafeInt(ceilDiv(landed, divisorForSell(sellForMargin)));
  if (quoted < UNDER_TEN_LIMIT_USD) return quoted + UNDER_TEN_BUMP_USD;
  return quoted;
}

function tieredFromLanded(landed: Frac): number {
  if (landed.n <= Z) {
    throw new Error("landed cost must be positive; refusing to invent a sell price");
  }
  const ceiling = quoteFromLanded(landed, 1) + UNDER_TEN_BUMP_USD;
  for (let sell = 1; sell <= ceiling; sell += 1) {
    if (sell >= quoteFromLanded(landed, sell)) return sell;
  }
  throw new Error("no non-undercutting sell");
}

/**
 * Smallest whole-dollar sell that does not undercut.
 * `landedUsd` is a decimal string so a binary float never enters the quote.
 */
export function tieredSellUsd(landedUsd: string): number {
  const landed = parsePositiveDecimal(landedUsd);
  if (!landed) {
    throw new Error("landed cost must be a positive decimal; refusing to invent a sell price");
  }
  return tieredFromLanded(landed);
}

/** Same padding as autolist `norm_ma`: S6 / S006 / s006 → S06. Non-mã text stays trimmed. */
function canonicalQuoteMa(raw: string): string {
  const code = raw.trim().toUpperCase();
  const match = code.match(/^([A-Z])(\d+)$/);
  if (!match?.[1] || match[2] == null) {
    return code;
  }
  return `${match[1]}${String(Number(match[2])).padStart(2, "0")}`;
}

/**
 * What a live catalog dollar would become under the tiered quote.
 * S06 stays $25, including S6 / S006 / s006. A missing cost keeps the live dollar.
 * Nothing is stored. Other short spellings (A1) stay invalid so they do not
 * become a quote for a different mã.
 */
export function wouldBeLiveUsd(input: IntakePriceInput): WouldBePrice {
  const trimmed = input.ma.trim().toUpperCase();
  const spelled = canonicalQuoteMa(trimmed);
  const ma = spelled === "S06" ? spelled : trimmed;
  if (!/^[A-Z][0-9]{2}$/.test(ma)) {
    throw new Error(`invalid mã ${input.ma}`);
  }
  if (!Number.isInteger(input.liveUsd) || input.liveUsd <= 0) {
    throw new Error(`live price for ${ma} must be a positive whole dollar`);
  }
  if (ma === "S06") {
    return {
      ma,
      liveUsd: input.liveUsd,
      wouldBeUsd: S06_LOCK_USD,
      applied: false,
      reason: "locked",
    };
  }
  const landed = landedFromCost({ ...input, ma });
  if (!landed) {
    return {
      ma,
      liveUsd: input.liveUsd,
      wouldBeUsd: input.liveUsd,
      applied: false,
      reason: "no-cost",
    };
  }
  return {
    ma,
    liveUsd: input.liveUsd,
    wouldBeUsd: tieredFromLanded(landed),
    applied: true,
    reason: "tiered",
  };
}
