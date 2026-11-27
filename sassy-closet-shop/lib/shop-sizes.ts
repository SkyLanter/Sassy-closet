import { ASIA_SIZE_LETTERS, type AsiaSizeLetter } from "@/lib/asia-size";

/** Letters that already appear on these looks, in Asia order. Never fills the gaps. */
export function collectShopSizes(
  products: readonly { sizes: readonly AsiaSizeLetter[] }[],
): AsiaSizeLetter[] {
  const present = new Set<string>();
  for (const product of products) {
    for (const size of product.sizes) {
      present.add(size);
    }
  }
  return ASIA_SIZE_LETTERS.filter((letter) => present.has(letter));
}

/** Tab badges for the home board. A selected size counts only looks that carry it. */
export function countLooksByType<T extends { type: string; sizes: readonly string[] }>(
  looks: readonly T[],
  types: readonly string[],
  size: string | null,
): Record<string, number> {
  const next: Record<string, number> = { all: 0 };
  for (const type of types) {
    let count = 0;
    for (const look of looks) {
      if (look.type !== type) {
        continue;
      }
      if (size !== null && !look.sizes.includes(size)) {
        continue;
      }
      count += 1;
    }
    next[type] = count;
    next.all += count;
  }
  return next;
}
