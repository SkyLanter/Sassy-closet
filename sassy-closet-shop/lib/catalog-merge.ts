import { asCatalogDocument } from "@/lib/product-parse";
import { siteId } from "@/lib/site-runtime";
import type { CatalogDocument, Product, ProductColor, ProductImageAsset } from "@/lib/types";

/**
 * Overlay incoming catalog.v1 onto a live document.
 * Matching mãs take the incoming row. Extra mãs on either side stay.
 * Does not invent mãs — both documents must already be parsed.
 */
export function mergeCatalogDocuments(
  base: CatalogDocument,
  incoming: CatalogDocument,
): CatalogDocument {
  const incomingByMa = new Map(incoming.products.map((product) => [product.ma, product]));
  const baseByMa = new Map(base.products.map((product) => [product.ma, product]));
  const order: string[] = [];
  for (const product of base.products) {
    if (!order.includes(product.ma)) {
      order.push(product.ma);
    }
  }
  for (const product of incoming.products) {
    if (!order.includes(product.ma)) {
      order.push(product.ma);
    }
  }
  const products: Product[] = order.map((ma) => {
    const next = incomingByMa.get(ma) ?? baseByMa.get(ma);
    if (!next) {
      throw new Error(`Merge lost mã ${ma}`);
    }
    return next;
  });
  return asCatalogDocument(products, incoming.settings, siteId());
}

export function mergeColorAssets(
  colors: ProductColor[],
  images: ProductImageAsset[],
  keepId: string,
  dropId: string,
): { colors: ProductColor[]; images: ProductImageAsset[] } {
  if (keepId === dropId) {
    throw new Error("Pick two different colors to merge");
  }
  const keep = colors.find((color) => color.id === keepId);
  const drop = colors.find((color) => color.id === dropId);
  if (!keep || !drop) {
    throw new Error("Both colors must exist on this mã");
  }
  return {
    colors: colors.filter((color) => color.id !== dropId),
    images: images.map((image) =>
      image.colorId === dropId ? { ...image, colorId: keepId } : image,
    ),
  };
}
