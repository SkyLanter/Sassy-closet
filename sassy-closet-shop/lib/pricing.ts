/**
 * Pricing math for the intake → sell pipeline. Pure functions, no I/O.
 *
 * Pipeline rule (locked): sell = ceil(landed / 0.7) at 30% margin, where
 * landed = CNY / FX + debox. FX default 6.723 (Boss-named), settable.
 * Under the 35% margin floor, or a blank sell → caption stays "Inbox giá".
 */

export const FX_DEFAULT = 6.723;
export const MARGIN_TARGET = 0.3;
export const MARGIN_FLOOR = 0.35;

/**
 * Locked Cainiao debox shipping share table (USD). Letters not listed here
 * are UNKNOWN — never invent a debox value for them.
 */
export const DEBOX_LOCKED_USD: Record<string, number> = {
  V: 7.5,
  Q: 7.5,
  D: 7.5,
};

export function deboxForLetter(letter: string): number | null {
  return DEBOX_LOCKED_USD[letter.trim().toUpperCase()] ?? null;
}

export type PricingInput = {
  /** Taobao list cost in CNY. Preferred when present. */
  costCny: number | null;
  /** Cost already in USD (used only when no CNY cost). */
  costUsd: number | null;
  /** CNY per USD. */
  fx: number;
  /** Cainiao debox share in USD. Null = unknown (never invent). */
  deboxUsd: number | null;
};

export type PricingBreakdown = {
  costUsd: number | null;
  landedUsd: number | null;
  /** ceil(landed / 0.7) — the 30% margin sell. */
  sellUsd: number | null;
  /** (sell - landed) / sell at the recommended sell. */
  marginAtSellPct: number | null;
};

function finitePositive(value: number | null): value is number {
  return typeof value === "number" && Number.isFinite(value) && value > 0;
}

export function calcPricing(input: PricingInput): PricingBreakdown {
  const empty: PricingBreakdown = {
    costUsd: null,
    landedUsd: null,
    sellUsd: null,
    marginAtSellPct: null,
  };
  let costUsd: number | null = null;
  if (finitePositive(input.costCny) && finitePositive(input.fx)) {
    costUsd = input.costCny / input.fx;
  } else if (finitePositive(input.costUsd)) {
    costUsd = input.costUsd;
  }
  if (costUsd === null) {
    return empty;
  }
  if (!finitePositive(input.deboxUsd)) {
    return { ...empty, costUsd };
  }
  const landed = costUsd + (input.deboxUsd as number);
  const sell = Math.ceil(landed / (1 - MARGIN_TARGET));
  return {
    costUsd,
    landedUsd: landed,
    sellUsd: sell,
    marginAtSellPct: (sell - landed) / sell,
  };
}

/**
 * Margin-floor guard for an explicit sell price. Under the 35% floor, or a
 * blank/invalid sell, the caption stays "Inbox giá".
 */
export function marginVerdict(landedUsd: number | null, sellUsd: number | null): "ok" | "inbox" {
  if (!finitePositive(landedUsd) || !finitePositive(sellUsd)) {
    return "inbox";
  }
  return (sellUsd - landedUsd) / sellUsd >= MARGIN_FLOOR ? "ok" : "inbox";
}

export function marginPct(landedUsd: number, sellUsd: number): number {
  return (sellUsd - landedUsd) / sellUsd;
}

export function formatUsd2(value: number | null): string {
  if (value === null || !Number.isFinite(value)) {
    return "—";
  }
  return `$${value.toFixed(2)}`;
}
