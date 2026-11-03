import { applyRecordedHubColors } from "@/lib/hub-colors";
import { KNOWN_SEED_MAS } from "@/lib/catalog-contract";
import { dropForeignHubFolderImages } from "@/lib/product-media";
import type { Product } from "@/lib/types";

export { applyRecordedHubColors };

/** Display names only — ids are hub slugs (`kem`, `cham-bi`). */
export const HUB_COLOR_NAMES: Readonly<Record<string, readonly string[]>> = {
  A01: ["Yellow", "Purple"],
  S01: ["White"],
  P01: ["Hoa"],
  P02: ["Judy", "Nick", "Stitch"],
  P03: ["Judy", "Nick", "Lotso", "Stitch", "Shin-chan"],
  P04: ["Kem"],
  P05: ["Peanuts", "Hello Kitty", "My Melody", "Cinnamoroll", "Kuromi"],
  K01: [],
  H01: [],
  A02: ["Off-white"],
};

/** Copy recorded hub slugs onto the ten. Titles, shop photos, prices untouched. */
export function applyHubColorNames(products: Product[]): Product[] {
  return products.map((product) => applyRecordedHubColors(dropForeignHubFolderImages(product)));
}

export function hubMas(): readonly string[] {
  return KNOWN_SEED_MAS;
}
