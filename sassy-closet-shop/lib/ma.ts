/** Allowed leading letters for Sassy Closet mãs. Do not invent letters. */
export const MA_LETTERS = [
  "A",
  "Q",
  "V",
  "D",
  "K",
  "G",
  "B",
  "P",
  "H",
  "J",
  "S",
  "O",
] as const;

export type MaLetter = (typeof MA_LETTERS)[number];

const LETTER_SET = new Set<string>(MA_LETTERS);

/** Mã = one allowed letter + digits (A01, K01, …). */
export function isValidMa(ma: string): boolean {
  const trimmed = ma.trim().toUpperCase();
  if (!/^[A-Z]\d+$/.test(trimmed)) {
    return false;
  }
  return LETTER_SET.has(trimmed[0] ?? "");
}

export function normalizeMa(ma: string): string {
  return ma.trim().toUpperCase();
}

export function maLetter(ma: string): MaLetter | null {
  const normalized = normalizeMa(ma);
  if (!isValidMa(normalized)) {
    return null;
  }
  return normalized[0] as MaLetter;
}

/** Stable mã order: letter (A Q V D …) then numeric (A01 < A02 < A11). */
export function compareMa(left: string, right: string): number {
  const a = normalizeMa(left);
  const b = normalizeMa(right);
  if (a === b) {
    return 0;
  }
  const letterA = maLetter(a);
  const letterB = maLetter(b);
  if (letterA && letterB && letterA !== letterB) {
    return MA_LETTERS.indexOf(letterA) - MA_LETTERS.indexOf(letterB);
  }
  const numA = Number.parseInt(a.slice(1), 10);
  const numB = Number.parseInt(b.slice(1), 10);
  if (Number.isFinite(numA) && Number.isFinite(numB) && numA !== numB) {
    return numA - numB;
  }
  return a.localeCompare(b, "en", { numeric: true });
}

/** Next unused mã for a letter (A02 present → A03). Never invents letters. */
export function nextMaForLetter(letter: MaLetter, existingMas: string[]): string {
  let max = 0;
  for (const ma of existingMas) {
    const normalized = normalizeMa(ma);
    if (maLetter(normalized) !== letter) {
      continue;
    }
    const n = Number.parseInt(normalized.slice(1), 10);
    if (Number.isFinite(n) && n > max) {
      max = n;
    }
  }
  return `${letter}${String(max + 1).padStart(2, "0")}`;
}
