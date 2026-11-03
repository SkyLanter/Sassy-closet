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
