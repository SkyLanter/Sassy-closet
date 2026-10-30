import type { MetadataRoute } from "next";

/**
 * HTML already sends noindex. robots.txt also keeps APIs and admin out.
 * `/` stays allowed so a crawler can see the noindex page. No sitemap.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api", "/api/", "/admin", "/admin/"],
    },
  };
}
