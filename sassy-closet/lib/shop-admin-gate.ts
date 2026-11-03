const SHOP_ADMIN_NEXT = /^\/admin\/shop(?:\/[A-Za-z0-9._~-]+)*(?:\?[A-Za-z0-9._~%=&+-]*)?$/u;

export function isShopAdminPage(pathname: string): boolean {
  return pathname === "/admin/shop" || pathname.startsWith("/admin/shop/");
}

export function isShopCatalogApi(pathname: string): boolean {
  return pathname === "/api/shop-catalog" || pathname.startsWith("/api/shop-catalog/");
}

/** Intake rows, CSV, mã cards, and shop tools. Open by direct link. */
export function isDirectLinkIntakeApi(pathname: string): boolean {
  return (
    pathname === "/api/submissions" ||
    pathname.startsWith("/api/submissions/") ||
    pathname === "/api/export" ||
    pathname.startsWith("/api/export/") ||
    pathname === "/api/ma" ||
    pathname.startsWith("/api/ma/")
  );
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
 * Every intake path is public, including shop tools and catalog APIs.
 * `pathname` and `hasSession` stay in the signature so callers do not grow a wall again.
 */
export function shopAdminGate(_pathname: string, _hasSession: boolean): ShopAdminGateDecision {
  return "public";
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
