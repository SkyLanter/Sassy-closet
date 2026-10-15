import { isOffLiveSell } from "@/lib/held-incomplete";
import { normalizeMa } from "@/lib/ma";
import { shopSafeProduct } from "@/lib/sell-contract";
import { toShopLook, type ShopLook } from "@/lib/shop-look";
import { SITE } from "@/lib/site";
import { defaultMessengerUrl } from "@/lib/site-runtime";
import { isLegacyAnnouncement } from "@/lib/trust-copy";
import type { Product, ProductStatus, SiteSettings } from "@/lib/types";

function messengerFallback(): string {
  return defaultMessengerUrl() || SITE.facebookPageUrl;
}

export function defaultSiteSettings(): SiteSettings {
  return {
    announcementLines: [...SITE.announcementLines],
    facebookPageUrl: messengerFallback(),
  };
}

export function parseFacebookPageUrl(value: unknown): string {
  if (typeof value !== "string" || !value.trim()) {
    return messengerFallback();
  }
  try {
    const url = new URL(value.trim());
    if (url.protocol !== "https:" && url.protocol !== "http:") {
      return messengerFallback();
    }
    return url.toString();
  } catch {
    return messengerFallback();
  }
}

export function parseSiteSettings(raw: unknown): SiteSettings {
  const fallback = defaultSiteSettings();
  if (typeof raw !== "object" || raw === null) {
    return fallback;
  }
  const row = raw as Record<string, unknown>;
  const linesRaw = row.announcementLines;
  const lines: string[] = [];
  if (Array.isArray(linesRaw)) {
    for (const item of linesRaw) {
      if (typeof item === "string") {
        const trimmed = item.trim();
        if (trimmed) {
          lines.push(trimmed);
        }
      }
    }
  }
  return {
    announcementLines:
      lines.length > 0 && !isLegacyAnnouncement(lines)
        ? lines.slice(0, 6)
        : fallback.announcementLines,
    facebookPageUrl: parseFacebookPageUrl(row.facebookPageUrl),
  };
}

export function isShopVisibleStatus(status: ProductStatus): boolean {
  switch (status) {
    case "available":
    case "hold":
      return true;
    case "sold":
      return false;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

export function shopVisibleProducts(products: Product[]): Product[] {
  return products
    .filter((product) => isShopVisibleStatus(product.status) && !isOffLiveSell(product.ma))
    .map(shopSafeProduct);
}

export function shopVisibleLooks(products: Product[]): ShopLook[] {
  return shopVisibleProducts(products).map(toShopLook);
}

export type PdpDecision = { status: 404 } | { status: 200; look: ShopLook };

/** Public PDP lookup. 404 is what `/m/[ma]` turns into `notFound()`. */
export function pdpDecision(products: Product[], ma: string): PdpDecision {
  const code = normalizeMa(ma);
  const look = shopVisibleLooks(products).find((item) => item.ma === code);
  if (!look) {
    return { status: 404 };
  }
  return { status: 200, look };
}

export function asksInboxPrice(status: ProductStatus): boolean {
  switch (status) {
    case "hold":
      return true;
    case "available":
    case "sold":
      return false;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

export function statusLabel(status: ProductStatus): string {
  switch (status) {
    case "available":
      return "Available";
    case "hold":
      return "Hold · Inbox for price";
    case "sold":
      return "Sold / Gone";
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}
