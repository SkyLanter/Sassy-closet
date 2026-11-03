/** Search engines stay off intake-style tools and APIs. Public lookbook HTML is separate. */
export const PRIVATE_ROBOTS_TAG = "noindex, nofollow, nosnippet";

export function isShopPrivateSurface(pathname: string): boolean {
  return (
    pathname === "/api" ||
    pathname.startsWith("/api/") ||
    pathname === "/admin" ||
    pathname.startsWith("/admin/")
  );
}
