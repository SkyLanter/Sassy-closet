export type SiteMode = "test" | "official";

const SITE_ID_PATTERN = /^[a-z0-9][a-z0-9-]{1,46}$/;

function firstEnv(...names: string[]): string {
  for (const name of names) {
    const value = process.env[name]?.trim();
    if (value) {
      return value;
    }
  }
  return "";
}

export function siteMode(): SiteMode {
  const raw = firstEnv("NEXT_PUBLIC_SITE_MODE", "SITE_MODE").toLowerCase();
  if (raw === "official") {
    return "official";
  }
  return "test";
}

export function siteId(): string {
  const raw = firstEnv("SITE_ID", "NEXT_PUBLIC_SITE_ID").toLowerCase();
  if (SITE_ID_PATTERN.test(raw)) {
    return raw;
  }
  return siteMode() === "official" ? "sassy-closet-official" : "sassy-closet-shop";
}

export function isSiteId(value: string): boolean {
  return SITE_ID_PATTERN.test(value.trim().toLowerCase());
}

/** Public shop origin. Empty when unset — never invent a Vercel hostname. */
export function publicShopUrl(): string {
  const raw = firstEnv("NEXT_PUBLIC_SHOP_URL", "SHOP_PUBLIC_URL");
  if (!raw) {
    return "";
  }
  try {
    const url = new URL(raw);
    if (url.protocol !== "https:" && url.protocol !== "http:") {
      return "";
    }
    return url.origin;
  } catch {
    return "";
  }
}

export function defaultMessengerUrl(): string {
  const raw = firstEnv("NEXT_PUBLIC_MESSENGER_URL", "MESSENGER_PAGE_URL");
  if (!raw) {
    return "";
  }
  try {
    const url = new URL(raw);
    if (url.protocol !== "https:" && url.protocol !== "http:") {
      return "";
    }
    return url.toString();
  } catch {
    return "";
  }
}

export type SiteRuntimeInfo = {
  id: string;
  mode: SiteMode;
  shopUrl: string;
  messengerUrl: string;
};

export function siteRuntimeInfo(): SiteRuntimeInfo {
  return {
    id: siteId(),
    mode: siteMode(),
    shopUrl: publicShopUrl(),
    messengerUrl: defaultMessengerUrl(),
  };
}
