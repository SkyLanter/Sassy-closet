import { KNOWN_SEED_MAS } from "@/lib/catalog-contract";
import { MA_LETTERS, type MaLetter } from "@/lib/ma";

/** Kit / PR #18 type words. Shop storage still uses the mã letter. */
const KIT_TYPE_TO_LETTER: Readonly<Record<string, MaLetter>> = {
  top: "A",
  pants: "Q",
  skirt: "V",
  dress: "D",
  jacket: "K",
  shoes: "G",
  bag: "B",
  accessory: "P",
  thermos: "P",
  hair: "H",
  jewelry: "J",
  set: "S",
  other: "O",
};

/** Recorded hub slug hex — admin boxes only. Not a mood board. */
export const HUB_SLUG_HEX: Readonly<Record<string, string>> = {
  kem: "#F4F0E8",
  xanh: "#1C2A4A",
  hoa: "#C4A484",
  do: "#8B3A3A",
  den: "#111111",
  hong: "#E8D5C4",
  "cham-bi": "#6B6B6B",
};

export function kitTypeToLetter(value: string): MaLetter | null {
  const trimmed = value.trim();
  if (trimmed.length === 1) {
    const upper = trimmed.toUpperCase();
    return (MA_LETTERS as readonly string[]).includes(upper) ? (upper as MaLetter) : null;
  }
  return KIT_TYPE_TO_LETTER[trimmed.toLowerCase()] ?? null;
}

export function sellTypeAccepted(maLetterValue: MaLetter, rawType: unknown): boolean {
  if (rawType === undefined || rawType === null || rawType === "") {
    return true;
  }
  if (typeof rawType !== "string") {
    return false;
  }
  const trimmed = rawType.trim();
  if (trimmed === maLetterValue) {
    return true;
  }
  return kitTypeToLetter(trimmed) === maLetterValue;
}

export function isHqDiskPhotoPath(src: string): boolean {
  const trimmed = src.trim();
  if (!trimmed) {
    return false;
  }
  if (/Documents\/Sassy Closet\/Photos/i.test(trimmed)) {
    return true;
  }
  if (/^https?:\/\/.*onedrive\.live\.com/i.test(trimmed)) {
    return true;
  }
  return /^[A-Z]\d{2,3}\/\d{3}\.(jpe?g|png|webp)$/i.test(trimmed);
}

export function isBlobDraftSrc(src: string): boolean {
  return src.trim().toLowerCase().startsWith("blob:");
}

export function assertKitAllowlist(raw: unknown): void {
  if (raw === undefined) {
    return;
  }
  if (!Array.isArray(raw)) {
    throw new Error("catalog.v1 allowlist must be an array of the ten hub mãs");
  }
  const mas = raw.map((item) => (typeof item === "string" ? item.trim().toUpperCase() : ""));
  if (mas.join(",") !== KNOWN_SEED_MAS.join(",")) {
    throw new Error(
      `catalog.v1 allowlist must be ${KNOWN_SEED_MAS.join(" ")} (got ${mas.join(" ") || "empty"})`,
    );
  }
}
