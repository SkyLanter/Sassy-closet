import { publicShopUrl } from "@/lib/site-runtime";

/** Vercel-provided host only — never invent a shop hostname in source. */
export function vercelPublicOrigin(): string {
  const raw =
    process.env.VERCEL_PROJECT_PRODUCTION_URL?.trim() || process.env.VERCEL_URL?.trim() || "";
  if (!raw) {
    return "";
  }
  if (raw.startsWith("http://") || raw.startsWith("https://")) {
    try {
      return new URL(raw).origin;
    } catch {
      return "";
    }
  }
  return `https://${raw.replace(/\/$/, "")}`;
}

/**
 * Absolute shop origin when we can resolve one without inventing a host.
 * Configured `NEXT_PUBLIC_SHOP_URL` wins; otherwise the Vercel deployment host.
 */
export function resolvableShopOrigin(): string {
  return publicShopUrl() || vercelPublicOrigin();
}
