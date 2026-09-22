import { assertLiveCatalogIntegrity, assertWrittenProductFacts } from "@/lib/catalog-integrity";
import { catalogShaOf } from "@/lib/catalog-sha";
import {
  writeLiveCatalog,
  writeLiveCatalogDocument,
  type CatalogWriteResult,
} from "@/lib/catalog-store";
import { refreshShop, publicPathsForMas } from "@/lib/refresh-shop";
import type { CatalogDocument, Product, SiteSettings } from "@/lib/types";

export type SaveReceipt = {
  ok: true;
  ma: string;
  blobWritten: true;
  catalogSha: string;
  updatedAt: string;
  revalidated: string[];
  products: Product[];
  settings: SiteSettings;
  nextMa?: string;
  renamedTo?: string;
};

function receiptFromWrite(
  written: CatalogWriteResult,
  revalidated: string[],
  extra?: { ma?: string; nextMa?: string; renamedTo?: string },
): SaveReceipt {
  if (!written.blobWritten) {
    throw new Error("Save did not write the live catalog.");
  }
  const catalogSha = written.catalogSha || catalogShaOf(written.document);
  const updatedAt = written.updatedAt || written.document.updatedAt;
  if (!updatedAt) {
    throw new Error("Save wrote a catalog without updatedAt.");
  }
  return {
    ok: true,
    ma: extra?.ma ?? extra?.nextMa ?? extra?.renamedTo ?? "",
    blobWritten: true,
    catalogSha,
    updatedAt,
    revalidated,
    products: written.document.products,
    settings: written.document.settings,
    nextMa: extra?.nextMa,
    renamedTo: extra?.renamedTo,
  };
}

export async function commitProductList(
  products: Product[],
  mas: string[],
  extra?: { ma?: string; nextMa?: string; renamedTo?: string },
): Promise<SaveReceipt> {
  assertLiveCatalogIntegrity(products);
  const written = await writeLiveCatalog(products);
  assertLiveCatalogIntegrity(written.document.products);
  const writtenMas = new Set(written.document.products.map((product) => product.ma));
  for (const product of products) {
    if (!writtenMas.has(product.ma)) {
      throw new Error("Save did not read back on the live catalog. The shop may still show the old list.");
    }
    assertWrittenProductFacts(written.document.products, product);
  }
  const fallbackPaths = publicPathsForMas(mas);
  let revalidated = fallbackPaths;
  try {
    const refreshed = await refreshShop(...mas);
    if (refreshed.length > 0) {
      revalidated = refreshed;
    }
  } catch (error) {
    console.error("Shop revalidate after catalog write failed.", error);
  }
  return receiptFromWrite(written, revalidated, extra);
}

export async function commitCatalogDocument(
  document: CatalogDocument,
  mas: string[],
  extra?: { ma?: string },
): Promise<SaveReceipt> {
  assertLiveCatalogIntegrity(document.products);
  const written = await writeLiveCatalogDocument(document);
  const fallbackPaths = publicPathsForMas(mas);
  let revalidated = fallbackPaths;
  try {
    const refreshed = await refreshShop(...mas);
    if (refreshed.length > 0) {
      revalidated = refreshed;
    }
  } catch (error) {
    console.error("Shop revalidate after catalog write failed.", error);
  }
  return receiptFromWrite(written, revalidated, extra);
}
