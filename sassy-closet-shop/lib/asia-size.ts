import type { MaLetter } from "@/lib/ma";

export const ASIA_SIZE_LETTERS = ["2XS", "XS", "S", "M", "L", "XL", "2XL"] as const;

export type AsiaSizeLetter = (typeof ASIA_SIZE_LETTERS)[number];

/** EU shoe sizes used on Taobao for G/O footwear. */
export const EU_SHOE_SIZES = ["34", "35", "36", "37", "38", "39", "40", "41", "42"] as const;
export type EuShoeSize = (typeof EU_SHOE_SIZES)[number];
export type ShopSize = AsiaSizeLetter | EuShoeSize;

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
    // Strict: keep Asia letters only (case-insensitive exact match).
    // "US M" is a US size reference — never map US sizes to Asia.
    // "XXS"/"XXL"/"3XL" are dropped, not normalized — only 2XS–2XL are valid.
    let next: ShopSize | null = null;
    if (isAsiaSizeLetter(upper)) {
      next = upper;
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
        `Size “${letter}” is not Asia (2XS–2XL) or EU shoe (34–42). Never US — never invent US size maps.`,
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
