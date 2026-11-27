import type { MaLetter } from "@/lib/ma";

export const ASIA_SIZE_LETTERS = ["2XS", "XS", "S", "M", "L", "XL", "2XL"] as const;

export type AsiaSizeLetter = (typeof ASIA_SIZE_LETTERS)[number];

/** EU shoe sizes used on Taobao for G/O footwear. */
export const EU_SHOE_SIZES = ["34", "35", "36", "37", "38", "39", "40", "41", "42"] as const;
export type EuShoeSize = (typeof EU_SHOE_SIZES)[number];
export type ShopSize = AsiaSizeLetter | EuShoeSize;

const ASIA_LETTER_RE = /^(2XS|XXS|XS|XXL|2XL|3XL|S|M|L|XL)\b/;
const ASIA_LETTER_WORD_RE = /\b(2XS|XXS|XS|XXL|2XL|3XL|S|M|L|XL)\b/;

export type FitCm = {
  bustChestCm: number | null;
  waistCm: number | null;
  lengthCm: number | null;
};

export function emptyFitCm(): FitCm {
  return { bustChestCm: null, waistCm: null, lengthCm: null };
}

export function isAsiaSizeLetter(value: string): value is AsiaSizeLetter {
  return (ASIA_SIZE_LETTERS as readonly string[]).includes(value);
}

export function isEuShoeSize(value: string): value is EuShoeSize {
  return (EU_SHOE_SIZES as readonly string[]).includes(value);
}

export function isShopSize(value: string): value is ShopSize {
  return isAsiaSizeLetter(value) || isEuShoeSize(value);
}

export function parseAsiaSizes(raw: unknown): ShopSize[] {
  if (raw === undefined || raw === null) {
    return [];
  }
  if (!Array.isArray(raw)) {
    throw new Error("sizes must be an array of Asia letters (2XS–2XL) or EU shoe (34–42)");
  }
  const seen = new Set<string>();
  const sizes: ShopSize[] = [];
  for (const item of raw) {
    if (typeof item !== "string" && typeof item !== "number") {
      continue;
    }
    const rawText = String(item).trim();
    const upper = rawText.toUpperCase();
    // Drop only a letter that is the US size ("US M", "M (US)", "美码 M").
    // A US note on a different value ("S (US 2-4)") still yields the Asia letter.
    if (asiaLetterIsUsSize(upper)) {
      continue;
    }
    // Asia main: accept exact letters OR extract from Taobao "S 建议80-90斤" / "M女【…】" / "XXL"
    const asiaMatch = upper.match(ASIA_LETTER_RE) ?? upper.match(ASIA_LETTER_WORD_RE);
    let next: ShopSize | null = null;
    if (asiaMatch) {
      let letter = asiaMatch[1];
      if (letter === "XXS") letter = "2XS";
      if (letter === "XXL" || letter === "3XL") letter = "2XL";
      if (isAsiaSizeLetter(letter)) {
        next = letter;
      }
    } else if (isEuShoeSize(rawText.replace(/[^0-9]/g, ""))) {
      // Footwear secondary only — never invent US
      next = rawText.replace(/[^0-9]/g, "") as ShopSize;
    }
    if (!next || seen.has(next)) {
      continue;
    }
    seen.add(next);
    sizes.push(next);
  }
  return sizes;
}

/**
 * The letter parseAsiaSizes would read is itself a US size.
 * US markers: "US", "美码", "美国码". A marker that annotates a digit
 * ("US 2-4", "US 6") is a note on that value, so the Asia letter stays.
 */
function asiaLetterIsUsSize(upper: string): boolean {
  const text = upper.replace(/（/g, "(").replace(/）/g, ")");
  if (!/\bUS\b/.test(text) && !/美国码|美码/.test(text)) {
    return false;
  }
  const found = ASIA_LETTER_RE.exec(text) ?? ASIA_LETTER_WORD_RE.exec(text);
  if (!found || found.index === undefined || !found[1]) {
    return false;
  }
  const start = found.index;
  const end = start + found[1].length;
  const before = text.slice(0, start);
  const after = text.slice(end);
  if (usMarkerImmediatelyBefore(before) || usLabelParenthetical(after)) {
    return true;
  }
  return bareUsMarkerFollowsLetter(after);
}

function usMarkerImmediatelyBefore(before: string): boolean {
  return /(?:\bUS|美国码|美码)\s*$/.test(before) || /\(\s*(?:US|美国码|美码)\s*\)\s*$/.test(before);
}

/** "(US)" / "(美码)" labels the letter. "(US 6)" does not — the number is the US value. */
function usLabelParenthetical(after: string): boolean {
  return /^\s*\(\s*(?:US|美国码|美码)\s*\)/.test(after);
}

/** "M US" / "M美码". "M US 6" keeps M: the marker annotates the digit. */
function bareUsMarkerFollowsLetter(after: string): boolean {
  const marker = /^\s*(US\b|美国码|美码)/.exec(after);
  if (!marker) {
    return false;
  }
  const rest = after.slice(marker[0].length);
  if (/^\s*\d/.test(rest) || /^\s*\([^)]*\d/.test(rest)) {
    return false;
  }
  return true;
}

/** Asia letters only, ordered 2XS–2XL. Drops EU shoe sizes. Never fills missing letters. */
export function catalogSizeLetters(sizes: readonly ShopSize[]): AsiaSizeLetter[] {
  return ASIA_SIZE_LETTERS.filter((letter) => sizes.includes(letter));
}

export function parseFitCm(raw: unknown): FitCm {
  if (raw === undefined || raw === null) {
    return emptyFitCm();
  }
  if (typeof raw !== "object" || Array.isArray(raw)) {
    throw new Error("fitCm must be { bustChestCm, waistCm, lengthCm }");
  }
  const row = raw as Record<string, unknown>;
  return {
    bustChestCm: parseStoredCm(row.bustChestCm ?? row.bust_chest),
    waistCm: parseStoredCm(row.waistCm ?? row.waist),
    lengthCm: parseStoredCm(row.lengthCm ?? row.length),
  };
}

function parseStoredCm(raw: unknown): number | null {
  if (raw === null || raw === undefined || raw === "") {
    return null;
  }
  if (typeof raw !== "number" || !Number.isFinite(raw) || raw <= 0) {
    return null;
  }
  return raw;
}

export function formatCm(value: number): string {
  return `${value} cm`;
}

export function hasAnyFitCm(fit: FitCm): boolean {
  return fit.bustChestCm !== null || fit.waistCm !== null || fit.lengthCm !== null;
}

export function assertAsiaSizesOnly(sizes: readonly string[]): void {
  for (const letter of sizes) {
    if (!isShopSize(letter)) {
      throw new Error(
        `Size “${letter}” is not Asia (2XS–2XL) or EU shoe (34–42). Never invent US maps.`,
      );
    }
  }
}

export function assertStoredFitCm(fit: FitCm): void {
  const keys = ["bustChestCm", "waistCm", "lengthCm"] as const;
  for (const key of keys) {
    const value = fit[key];
    if (value === null) {
      continue;
    }
    if (!Number.isFinite(value) || value <= 0) {
      throw new Error("Fit cm must be a stored number or blank. Do not invent from a size letter.");
    }
  }
}

/** PK / hair / thermos / jewelry / bags: hide the letter row when nothing is stored. */
export function hidesEmptyAsiaLetterRow(type: MaLetter): boolean {
  switch (type) {
    case "P":
    case "H":
    case "J":
    case "B":
      return true;
    case "A":
    case "Q":
    case "V":
    case "K":
    case "G":
    case "S":
    case "O":
    case "D":
      return false;
    default: {
      const _exhaustive: never = type;
      return _exhaustive;
    }
  }
}

export function inboxForFitLine(ma: string): string {
  return `Inbox ${ma} for fit`;
}
