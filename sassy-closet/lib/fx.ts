import { readMoney, type MoneySide } from "./money-text";

/** Weekly store rate: 1 USD = usdCny ¥ CNY. */

export function formatMoney(n: number): string {
  if (!Number.isFinite(n)) return "";
  return (Math.round((n + Number.EPSILON) * 100) / 100).toFixed(2);
}

/**
 * Convert one money field using the weekly USD→CNY rate.
 * Empty source clears the other field (`""`). A typed zero writes `0.00`
 * so the paired field does not keep the previous price. Garbled text,
 * mid-typing, or a bad rate returns `null` so the other field is left alone.
 */
export function convertCnyToUsd(cny: string, usdCny: number): string | null {
  return convertMoney(cny, "CNY", usdCny, (amount, rate) => amount / rate);
}

export function convertUsdToCny(usd: string, usdCny: number): string | null {
  return convertMoney(usd, "USD", usdCny, (amount, rate) => amount * rate);
}

function convertMoney(
  raw: string,
  side: MoneySide,
  usdCny: number,
  apply: (amount: number, rate: number) => number,
): string | null {
  const parsed = readMoney(raw, side);
  if (parsed.kind === "blank") return "";
  if (parsed.kind !== "amount") return null;
  if (!Number.isFinite(usdCny) || usdCny <= 0) return null;
  return formatMoney(apply(parsed.value, usdCny));
}
