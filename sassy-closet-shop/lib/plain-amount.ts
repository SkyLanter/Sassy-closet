/** Thousands groups only, such as 1,200 or 1,200.50. */
const THOUSANDS = /^\d{1,3}(?:,\d{3})+(?:\.\d+)?$/;
const PLAIN = /^\d+(?:\.\d+)?$/;
const TRAILING_DOT_INTEGER = /^\d+\.$/;
const TRAILING_DOT_THOUSANDS = /^\d{1,3}(?:,\d{3})+\.$/;

/**
 * Plain non-negative amount.
 * A comma is a thousands separator, or the text is not an amount.
 * Exponents, hex, signs, and other marks are not amounts.
 */
export function plainAmount(raw: string): number | null {
  const trimmed = raw.trim();
  if (!trimmed) {
    return null;
  }

  let text = trimmed;
  if (TRAILING_DOT_INTEGER.test(text) || TRAILING_DOT_THOUSANDS.test(text)) {
    text = text.slice(0, -1);
  }

  if (text.includes(",")) {
    if (!THOUSANDS.test(text)) {
      return null;
    }
    text = text.replace(/,/g, "");
  }

  if (!PLAIN.test(text)) {
    return null;
  }

  const value = Number(text);
  if (!Number.isFinite(value) || value < 0) {
    return null;
  }

  const dot = text.indexOf(".");
  const fraction = dot === -1 ? "" : text.slice(dot + 1);
  if (fraction.length > 2) {
    return value;
  }

  const whole = dot === -1 ? text : text.slice(0, dot);
  const centsDigits = `${whole}${fraction.padEnd(2, "0")}`.replace(/^0+(?=\d)/, "");
  const maxSafeCents = String(Number.MAX_SAFE_INTEGER);
  if (
    centsDigits.length > maxSafeCents.length ||
    (centsDigits.length === maxSafeCents.length && centsDigits > maxSafeCents)
  ) {
    return null;
  }

  const cents = Number(centsDigits);
  if (!Number.isSafeInteger(cents) || Math.round(value * 100) !== cents) {
    return null;
  }
  return value;
}
