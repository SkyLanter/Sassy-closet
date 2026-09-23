import type { MetadataRoute } from "next";
import { resolvableShopOrigin } from "@/lib/shop-origin";

/**
 * Test HTML stays noindex (lasting TEST). robots.txt still exists so
 * Facebook / share crawlers can fetch catalog URLs. Do not Disallow `/`.
 */
export default function robots(): MetadataRoute.Robots {
  const origin = resolvableShopOrigin();
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/admin/", "/api/"],
    },
    sitemap: origin ? `${origin}/sitemap.xml` : undefined,
  };
}
