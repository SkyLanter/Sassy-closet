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
    .filter((product) => isShopVisibleStatus(product.status))
    .map(shopSafeProduct);
}

export function shopVisibleLooks(products: Product[]): ShopLook[] {
  // Shop cards need photos — photo-less products stay in the admin catalog
  // but never list as shoppable looks. Editorial heroes (D02) are homepage
  // only, never duplicated as shop looks.
  return shopVisibleProducts(products)
    .filter((product) => product.images.length > 0)
    .filter((product) => !product.editorialHero)
    .map(toShopLook);
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
