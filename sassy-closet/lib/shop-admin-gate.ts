const SHOP_ADMIN_NEXT = /^\/admin\/shop(?:\/[A-Za-z0-9._~-]+)*(?:\?[A-Za-z0-9._~%=&+-]*)?$/u;

export function isShopAdminPage(pathname: string): boolean {
  return pathname === "/admin/shop" || pathname.startsWith("/admin/shop/");
}

export function isShopCatalogApi(pathname: string): boolean {
  return pathname === "/api/shop-catalog" || pathname.startsWith("/api/shop-catalog/");
}

export function isShopAdminLoginPath(pathname: string): boolean {
  return pathname === "/admin/shop/login";
}

export function isShopAdminLoginApi(pathname: string): boolean {
  return pathname === "/api/shop-catalog/login";
}

export function isShopAdminLogoutApi(pathname: string): boolean {
  return pathname === "/api/shop-catalog/logout";
}

export type ShopAdminGateDecision = "public" | "allow" | "deny";

/**
 * `public` — intake pages, including the CSV export at /admin.
 * `allow` — login, logout, or a shop-tools route with a valid session.
 * `deny` — shop tools without a session.
 */
export function shopAdminGate(pathname: string, hasSession: boolean): ShopAdminGateDecision {
  const page = isShopAdminPage(pathname);
  const api = isShopCatalogApi(pathname);
  if (!page && !api) {
    return "public";
  }
  if (isShopAdminLoginPath(pathname) || isShopAdminLoginApi(pathname) || isShopAdminLogoutApi(pathname)) {
    return "allow";
  }
  if (hasSession) {
    return "allow";
  }
  return "deny";
}

/** Only same-origin shop-tools paths. Anything else becomes the desk. */
export function safeShopAdminNext(raw: string | null | undefined): string {
  if (!raw || raw.length > 200) {
    return "/admin/shop";
  }
  if (raw.includes("..") || raw.includes("\\") || raw.includes("//")) {
    return "/admin/shop";
  }
  if (!SHOP_ADMIN_NEXT.test(raw)) {
    return "/admin/shop";
  }
  const pathOnly = raw.split("?")[0] ?? "";
  if (pathOnly === "/admin/shop/login" || pathOnly.startsWith("/admin/shop/login/")) {
    return "/admin/shop";
  }
  return raw;
}
