/**
 * Intake data someone can open with the link alone: no session, no Authorization.
 * Search engines stay out via X-Robots-Tag. These paths are not in the sitemap or nav.
 */
export const INTAKE_DIRECT_LINK_HEADERS: Record<string, string> = {
  "Cache-Control": "private, no-store, no-cache, max-age=0, must-revalidate",
  "X-Robots-Tag": "noindex, nofollow",
};

export const INTAKE_DIRECT_LINK_SOURCES = [
  "/api/submissions",
  "/api/submissions/:path*",
  "/api/export",
  "/api/export/:path*",
  "/api/ma/:path*",
] as const;
