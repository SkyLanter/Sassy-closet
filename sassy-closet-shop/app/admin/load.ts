import { getCatalogStorageInfo } from "@/lib/catalog-store";
import { getCatalogDocumentUncached, getCatalogReadSource } from "@/lib/products";
import { siteRuntimeInfo, type SiteRuntimeInfo } from "@/lib/site-runtime";
import type { CatalogStorageInfo } from "@/lib/storage-info";
import type { Product, SiteSettings } from "@/lib/types";

export type AdminPageData = {
  products: Product[];
  settings: SiteSettings;
  storage: CatalogStorageInfo;
  site: SiteRuntimeInfo;
};

export async function loadAdminPageData(): Promise<AdminPageData> {
  const document = await getCatalogDocumentUncached();
  const reading = await getCatalogReadSource();
  return {
    products: document.products,
    settings: document.settings,
    storage: { ...getCatalogStorageInfo(), reading },
    site: siteRuntimeInfo(),
  };
}
