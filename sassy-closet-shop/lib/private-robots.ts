import { NO_STORE_HEADERS } from "./http-no-store";

/** Search engines stay off intake-style tools and APIs. Public lookbook HTML is separate. */
export const PRIVATE_ROBOTS_TAG = "noindex, nofollow, nosnippet";

/** Plain 404 for held mãs, missing photos, and unknown share cards. */
export const PRIVATE_NOT_FOUND_HEADERS = {
  ...NO_STORE_HEADERS,
  "content-type": "text/plain; charset=utf-8",
  "X-Robots-Tag": PRIVATE_ROBOTS_TAG,
} as const;

export function isShopPrivateSurface(pathname: string): boolean {
  return (
    pathname === "/api" ||
    pathname.startsWith("/api/") ||
    pathname === "/admin" ||
    pathname.startsWith("/admin/")
  );
}
