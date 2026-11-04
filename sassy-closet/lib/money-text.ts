/**
 * Read a typed money field without inventing a price.
 *
 * Blank stays blank. Yen, dollars, fullwidth digits, thousands commas, and a
 * trailing dot fold into canonical digits. A thousands group starts at 1–999,
 * so 0,025 is not 25. Scientific notation, hex, and any other garbage stay
 * garbage.
 */

const PLAIN_AMOUNT = /^\d+(?:\.\d+)?$/;
const THOUSANDS = /^[1-9]\d{0,2}(?:,\d{3})+(?:\.\d+)?$/;
const THOUSANDS_INT = /^[1-9]\d{0,2}(?:,\d{3})+$/;
const DIGITS = /^\d+$/;

const USD_LEAD = /^(?:\$|usd)\s*/i;
const USD_TRAIL = /\s*(?:\$|usd)$/i;
const CNY_LEAD = /^(?:\u00A5|\uFFE5|\u5143|rmb|cny)\s*/i;
const CNY_TRAIL = /\s*(?:\u00A5|\uFFE5|\u5143|rmb|cny)$/i;

export type MoneySide = "USD" | "CNY";

export type MoneyRead =
  | { kind: "blank" }
  | { kind: "amount"; text: string; value: number }
  | { kind: "garbled"; text: string };

export function readMoney(raw: string, side: MoneySide): MoneyRead {
  const visible = visibleMoney(raw);
  if (visible === "") return { kind: "blank" };
  const parsed = parseLoose(visible, side);
  if (!parsed) return { kind: "garbled", text: visible };
  return { kind: "amount", text: parsed.text, value: parsed.value };
}

/** Blank stores nothing. A folded amount stores canonical digits. Garbage is trimmed only. */
export function moneyForStore(raw: string, side: MoneySide): string {
  const read = readMoney(raw, side);
  switch (read.kind) {
    case "blank":
      return "";
    case "garbled":
      return read.text;
    case "amount": {
      const visible = visibleMoney(raw);
      if (PLAIN_AMOUNT.test(visible)) return visible;
      return read.text;
    }
    default: {
      const neverRead: never = read;
      throw new Error(`unknown money read ${String(neverRead)}`);
    }
  }
}

function visibleMoney(raw: string): string {
  return raw.replaceAll("\uFEFF", "").trim();
}

function parseLoose(text: string, side: MoneySide): { text: string; value: number } | null {
  const { lead, trail } = patterns(side);
  const fromLead = stripEdge(text, lead, "lead");
  if (fromLead != null) {
    const parsed = parseAmountBody(foldMoneyChars(fromLead));
    if (parsed) return parsed;
  }
  const fromTrail = stripEdge(text, trail, "trail");
  if (fromTrail != null) {
    const parsed = parseAmountBody(foldMoneyChars(fromTrail));
    if (parsed) return parsed;
  }
  return parseAmountBody(foldMoneyChars(text));
}

function patterns(side: MoneySide): { lead: RegExp; trail: RegExp } {
  switch (side) {
    case "USD":
      return { lead: USD_LEAD, trail: USD_TRAIL };
    case "CNY":
      return { lead: CNY_LEAD, trail: CNY_TRAIL };
    default: {
      const neverSide: never = side;
      throw new Error(`unknown money side ${String(neverSide)}`);
    }
  }
}

function stripEdge(text: string, pattern: RegExp, edge: "lead" | "trail"): string | null {
  const match = text.match(pattern);
  if (!match || match[0].length === 0) return null;
  if (edge === "lead") return text.slice(match[0].length);
  return text.slice(0, -match[0].length);
}

function foldMoneyChars(text: string): string {
  return text
    .replace(/[\uFF10-\uFF19]/g, (digit) => String.fromCharCode(digit.charCodeAt(0) - 0xff10 + 0x30))
    .replace(/[\uFF0E\u3002]/g, ".")
    .replace(/\uFF0C/g, ",");
}

function parseAmountBody(folded: string): { text: string; value: number } | null {
  if (folded === "") return null;
  let body = folded;
  if (body.endsWith(".")) {
    const head = body.slice(0, -1);
    if (DIGITS.test(head) || THOUSANDS_INT.test(head)) body = head;
  }
  if (body.includes(",")) {
    if (!THOUSANDS.test(body)) return null;
    body = body.replaceAll(",", "");
  }
  if (!PLAIN_AMOUNT.test(body)) return null;
  const value = Number(body);
  if (!Number.isFinite(value)) return null;
  return { text: body, value };
}
