import { TYPE_LABELS } from "@/lib/catalog";
import { MA_LETTERS, type MaLetter } from "@/lib/ma";

const CATALOG_LETTERS = new Set<string>(MA_LETTERS);

/**
 * One complementary piece type for a catalog letter.
 * Every result is a letter already in the catalog. No mã is minted.
 */
export type OutfitBundleSuggestion = {
  letter: MaLetter;
  piece: MaLetter;
  pieceVn: string;
  pieceEn: string;
};

export function isCatalogLetter(value: string): value is MaLetter {
  return CATALOG_LETTERS.has(value);
}

/** A single catalog letter, or null when the input is a mã or an unknown letter. */
export function suggestOutfitBundle(letter: string): OutfitBundleSuggestion | null {
  const trimmed = letter.trim();
  if (trimmed.length !== 1) {
    return null;
  }
  const upper = trimmed.toUpperCase();
  if (!isCatalogLetter(upper)) {
    return null;
  }
  const piece = complementaryPiece(upper);
  const labels = TYPE_LABELS[piece];
  return {
    letter: upper,
    piece,
    pieceVn: labels.vn,
    pieceEn: labels.en,
  };
}

function complementaryPiece(letter: MaLetter): MaLetter {
  switch (letter) {
    case "S":
      return "G";
    case "A":
      return "Q";
    case "D":
      return "G";
    case "Q":
      return "A";
    case "V":
      return "A";
    case "K":
      return "A";
    case "G":
      return "D";
    case "B":
      return "D";
    case "P":
      return "A";
    case "H":
      return "A";
    case "J":
      return "D";
    case "O":
      return "P";
    default: {
      const unknown: never = letter;
      throw new Error(`Unknown catalog letter ${String(unknown)}`);
    }
  }
}
