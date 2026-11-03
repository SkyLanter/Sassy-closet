import { isKnownSeedMa } from "@/lib/catalog-contract";
import type { Product, ProductColor, ProductImageAsset } from "@/lib/types";

/** Gallery helpers need mã + colors + images only — never status. */
export type MaMedia = {
  ma: string;
  colors: ProductColor[];
  images: ProductImageAsset[];
};

/**
 * Hub ten never render another hub mã’s `/products/{MA}/` file.
 * Blob `/uploads/`, https URLs, and extra-mã folders (rename A04 → A03) stay.
 */
export function srcBelongsToMa(src: string, ma: string): boolean {
  const trimmed = src.trim();
  if (!trimmed) {
    return false;
  }
  const pathOnly = trimmed.split("?")[0] ?? trimmed;
  const match = pathOnly.match(/\/products\/([^/]+)\//i);
  if (!match) {
    return true;
  }
  const folder = match[1];
  if (folder === ma) {
    return true;
  }
  return !isKnownSeedMa(folder);
}

export function ownMaImages(product: MaMedia): ProductImageAsset[] {
  return product.images.filter((image) => srcBelongsToMa(image.src, product.ma));
}

export function dropForeignHubFolderImages(product: Product): Product {
  const images = ownMaImages(product);
  if (images.length === product.images.length) {
    return product;
  }
  return { ...product, images };
}

/** Unique srcs so a watery roll never clones cover.jpg as a fake neighbor. */
export function uniqueImageSrcs(images: ProductImageAsset[]): ProductImageAsset[] {
  const seen = new Set<string>();
  const next: ProductImageAsset[] = [];
  for (const image of images) {
    if (seen.has(image.src)) {
      continue;
    }
    seen.add(image.src);
    next.push(image);
  }
  return next;
}

export function coverSrc(product: MaMedia): string | undefined {
  return ownMaImages(product)[0]?.src;
}

/**
 * This mã only: tagged-to-color ∪ untagged/shared.
 * Unknown color ids stay empty — never another mã’s palette, never `?? coverSrc`.
 */
export function imagesForColor(
  product: MaMedia,
  colorId: string | null,
): ProductImageAsset[] {
  const usable = ownMaImages(product);
  if (colorId === null) {
    return usable;
  }
  if (!product.colors.some((color) => color.id === colorId)) {
    return [];
  }
  return usable.filter((image) => image.colorId === colorId || image.colorId === null);
}

export function coverSrcForColor(product: MaMedia, colorId: string | null): string | undefined {
  return imagesForColor(product, colorId)[0]?.src;
}

export function imagesTaggedToColor(
  images: ProductImageAsset[],
  colorId: string,
): ProductImageAsset[] {
  return images.filter((image) => image.colorId === colorId && image.src.trim());
}
