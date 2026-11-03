export type ShopDeskPriceResult =
  | { ok: true; priceUsd: number | null }
  | { ok: false; error: string };

const MAX_USD = 100000;
const PLAIN_USD = /^(?:0|[1-9]\d*)(?:\.\d{1,2})?$/;

function invalidPrice(ma: string): ShopDeskPriceResult {
  return { ok: false, error: `Mã ${ma} has an invalid USD price.` };
}

function centsFromLiteral(literal: string): number | null {
  const dot = literal.indexOf(".");
  const whole = dot === -1 ? literal : literal.slice(0, dot);
  const fraction = dot === -1 ? "" : literal.slice(dot + 1);
  const dollars = Number(whole);
  if (!Number.isSafeInteger(dollars)) {
    return null;
  }
  const fracCents = fraction.length === 0 ? 0 : fraction.length === 1 ? Number(fraction) * 10 : Number(fraction);
  const cents = dollars * 100 + fracCents;
  if (!Number.isSafeInteger(cents) || cents < 0 || cents > MAX_USD * 100) {
    return null;
  }
  return cents;
}

export function parseShopDeskPrice(raw: string, ma: string): ShopDeskPriceResult {
  const trimmed = raw.trim();
  if (trimmed === "") {
    return { ok: true, priceUsd: null };
  }
  if (!PLAIN_USD.test(trimmed)) {
    return invalidPrice(ma);
  }
  const cents = centsFromLiteral(trimmed);
  if (cents === null) {
    return invalidPrice(ma);
  }
  return { ok: true, priceUsd: cents / 100 };
}
