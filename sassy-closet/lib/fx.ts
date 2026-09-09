/** Weekly store rate: 1 USD = usdCny ¥ CNY. */

export function formatMoney(n: number): string {
  if (!Number.isFinite(n)) return "";
  return (Math.round((n + Number.EPSILON) * 100) / 100).toFixed(2);
}

/**
 * Convert one money field using the weekly USD→CNY rate.
 * Empty source clears the other field (`""`). Invalid mid-typing or a bad
 * rate returns `null` so the other field is left alone.
 */
export function convertCnyToUsd(cny: string, usdCny: number): string | null {
  return convertMoney(cny, usdCny, (amount, rate) => amount / rate);
}

export function convertUsdToCny(usd: string, usdCny: number): string | null {
  return convertMoney(usd, usdCny, (amount, rate) => amount * rate);
}

function convertMoney(
  raw: string,
  usdCny: number,
  apply: (amount: number, rate: number) => number,
): string | null {
  const trimmed = raw.trim();
  if (trimmed === "") return "";
  const amount = Number(trimmed);
  if (!Number.isFinite(amount) || !Number.isFinite(usdCny) || usdCny <= 0) return null;
  return formatMoney(apply(amount, usdCny));
}
