import { connection } from "next/server";
import { CATALOG_CACHE_TAG } from "@/lib/catalog-tag";
import { readLiveCatalogDocument, readLiveCatalogRecord } from "@/lib/catalog-store";
import { normalizeMa, type MaLetter } from "@/lib/ma";
import { shopVisibleLooks } from "@/lib/site-settings";
import type { CatalogBackend } from "@/lib/storage-info";
import type { CatalogDocument, Product, SiteSettings } from "@/lib/types";
import { sortByPopular } from "@/lib/popular-rank";
import type { ShopLook } from "@/lib/shop-look";

export { CATALOG_CACHE_TAG };

const FEATURED_TYPE_ORDER: MaLetter[] = ["A", "S", "P", "K", "H"];

async function loadRequestCatalog(): Promise<CatalogDocument> {
  await connection();
  return readLiveCatalogDocument();
}

export async function getCatalogDocument(): Promise<CatalogDocument> {
  return loadRequestCatalog();
}

export async function getCatalogDocumentUncached(): Promise<CatalogDocument> {
  return loadRequestCatalog();
}

export async function getCatalogReadSource(): Promise<CatalogBackend> {
  await connection();
  const record = await readLiveCatalogRecord();
  return record.source;
}

export async function getProducts(): Promise<ShopLook[]> {
  const document = await getCatalogDocument();
  return sortByPopular(shopVisibleLooks(document.products));
}

export async function getAdminProducts(): Promise<Product[]> {
  const document = await getCatalogDocumentUncached();
  return document.products;
}

export async function getProductsUncached(): Promise<Product[]> {
  return getAdminProducts();
}

export async function getSiteSettings(): Promise<SiteSettings> {
  const document = await getCatalogDocument();
  return document.settings;
}

export async function getSiteSettingsUncached(): Promise<SiteSettings> {
  const document = await getCatalogDocumentUncached();
  return document.settings;
}

export async function getProduct(ma: string): Promise<ShopLook | undefined> {
  const normalized = normalizeMa(ma);
  const products = await getProducts();
  return products.find((product) => product.ma === normalized);
}

export function catalogTypesFrom(products: Array<{ type: MaLetter }>): MaLetter[] {
  const present = new Set(products.map((product) => product.type));
  const ordered = FEATURED_TYPE_ORDER.filter((type) => present.has(type));
  for (const product of products) {
    if (!ordered.includes(product.type)) {
      ordered.push(product.type);
    }
  }
  return ordered;
}

export async function getCatalogTypes(): Promise<MaLetter[]> {
  return catalogTypesFrom(await getProducts());
}

export async function getProductsByType(type: MaLetter): Promise<ShopLook[]> {
  const products = await getProducts();
  return products.filter((product) => product.type === type);
}
