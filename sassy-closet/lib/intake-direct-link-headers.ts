/**
 * Intake data someone can open with the link alone: no session, no Authorization.
 * Search engines stay out via X-Robots-Tag. These paths are not in the sitemap or nav.
 */
export const INTAKE_DIRECT_LINK_HEADERS: Record<string, string> = {
  "Cache-Control": "private, no-store, no-cache, max-age=0, must-revalidate",
  "X-Robots-Tag": "noindex, nofollow, nosnippet",
};

/** HTML pages that list intake rows or the CSV. Same robots intent as the data APIs. */
export const INTAKE_LISTING_ROBOTS = {
  index: false,
  follow: false,
  nosnippet: true,
} as const;

/** Every `/api` and `/admin` URL, including health, submissions, export, and mã cards. */
export function isIntakePrivateSurface(pathname: string): boolean {
  return (
    pathname === "/api" ||
    pathname.startsWith("/api/") ||
    pathname === "/admin" ||
    pathname.startsWith("/admin/")
  );
}

export const INTAKE_DIRECT_LINK_SOURCES = [
  "/api",
  "/api/:path*",
  "/admin",
  "/admin/:path*",
] as const;
