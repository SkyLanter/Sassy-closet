import type { MetadataRoute } from "next";
import { categoryHref } from "@/lib/categories";
import { readLiveCatalogDocument } from "@/lib/catalog-store";
import { catalogTypesFrom } from "@/lib/products";
import { coverSrc } from "@/lib/product-media";
import { shopVisibleProducts } from "@/lib/site-settings";
import { resolvableShopOrigin } from "@/lib/shop-origin";
import { normalizeMa } from "@/lib/ma";

export const dynamic = "force-dynamic";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const origin =
    resolvableShopOrigin() || (process.env.VERCEL !== "1" ? "http://127.0.0.1:43147" : "");
  if (!origin) {
    return [];
  }
  const document = await readLiveCatalogDocument();
  const products = shopVisibleProducts(document.products);
  const types = catalogTypesFrom(products);
  const lastModified = document.updatedAt ? new Date(document.updatedAt) : new Date();
  return [
    { url: origin, lastModified },
    { url: `${origin}/how-to-buy`, lastModified },
    { url: `${origin}/meetup-ship`, lastModified },
    ...types.map((type) => ({
      url: `${origin}${categoryHref(type)}`,
      lastModified,
    })),
    ...products.map((product) => {
      const ma = normalizeMa(product.ma);
      const cover = coverSrc(product);
      const images = cover
        ? [cover.startsWith("http") ? cover : `${origin}${cover}`]
        : undefined;
      return {
        url: `${origin}/m/${ma}`,
        lastModified,
        images,
      };
    }),
  ];
}
