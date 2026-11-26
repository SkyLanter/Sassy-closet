import type { MetadataRoute } from "next";
import { categoryHref } from "@/lib/categories";
import { readLiveCatalogDocumentForShop as readLiveCatalogDocument } from "@/lib/catalog-store";
import { catalogTypesFrom } from "@/lib/products";
import { coverSrc } from "@/lib/product-media";
import { shopVisibleProducts } from "@/lib/site-settings";
import { resolvableShopOrigin } from "@/lib/shop-origin";
import { canonicalMaSpelling } from "@/lib/ma";

export const dynamic = "force-dynamic";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const origin =
    resolvableShopOrigin() || (process.env.VERCEL !== "1" ? "http://127.0.0.1:43147" : "");
  if (!origin) {
    return [];
  }
  const document = await readLiveCatalogDocument();
  // A look with no photo of its own is not a shop page (README), so it is not
  // a sitemap URL either. `coverSrc` is that same own-photo check.
  const products = shopVisibleProducts(document.products).filter((product) => coverSrc(product));
  const types = catalogTypesFrom(products);
  const lastModified = document.updatedAt ? new Date(document.updatedAt) : new Date();
  return [
    { url: origin, lastModified },
    ...types.map((type) => ({
      url: `${origin}${categoryHref(type)}`,
      lastModified,
    })),
    ...products.map((product) => {
      const ma = canonicalMaSpelling(product.ma);
      const cover = coverSrc(product) as string;
      const images = [cover.startsWith("http") ? cover : `${origin}${cover}`];
      return {
        url: `${origin}/m/${ma}`,
        lastModified,
        images,
      };
    }),
  ];
}
