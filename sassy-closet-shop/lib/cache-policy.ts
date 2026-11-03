/**
 * Caching policy for the public sell site (draft PR 04 — Vercel transfer).
 *
 * Goal: stop re-reading the Blob catalog and re-sending every photo on every
 * page view, without changing prices, products, or held-mã logic.
 *
 * - Catalog memo: one Blob/KV catalog read per server instance per
 *   CATALOG_MEMO_TTL_MS. Any catalog write on this instance clears it.
 * - Product photos (/products/<mã>/<file>): CDN-cached; browsers keep 1h.
 * - Public shop HTML: short CDN cache with stale-while-revalidate.
 *   Browser copy is always revalidated, so the window is CDN-only.
 * - Admin, API, 404s and search (?q=) stay no-store.
 */

export const CATALOG_MEMO_TTL_MS = 30_000;

export const IMAGE_BROWSER_MAX_AGE_S = 3_600; // 1 hour
export const IMAGE_CDN_MAX_AGE_S = 86_400; // 1 day
export const IMAGE_STALE_WHILE_REVALIDATE_S = 604_800; // 7 days

export const HTML_CDN_CACHE_ENABLED = true;
export const HTML_CDN_MAX_AGE_S = 60;
export const HTML_STALE_WHILE_REVALIDATE_S = 300;

export const NO_STORE_VALUE = "private, no-store, no-cache, max-age=0, must-revalidate";

export function productImageCacheHeaders(): Record<string, string> {
  const cdn = `public, s-maxage=${IMAGE_CDN_MAX_AGE_S}, stale-while-revalidate=${IMAGE_STALE_WHILE_REVALIDATE_S}`;
  return {
    "Cache-Control": `public, max-age=${IMAGE_BROWSER_MAX_AGE_S}, s-maxage=${IMAGE_CDN_MAX_AGE_S}, stale-while-revalidate=${IMAGE_STALE_WHILE_REVALIDATE_S}`,
    "CDN-Cache-Control": cdn,
    "Vercel-CDN-Cache-Control": cdn,
  };
}

const PUBLIC_HTML_PATHS: RegExp[] = [
  /^\/$/,
  /^\/m\/[^/]+\/?$/,
  /^\/c\/[^/]+\/?$/,
  /^\/how-to-buy\/?$/,
  /^\/meetup-ship\/?$/,
];

export type HtmlCacheRequest = {
  method: string;
  pathname: string;
  search: URLSearchParams;
  headers: { get(name: string): string | null };
};

/** True only for anonymous public page GETs that are safe to share at the CDN. */
export function isCdnCacheableHtml(req: HtmlCacheRequest): boolean {
  if (!HTML_CDN_CACHE_ENABLED) return false;
  if (req.method !== "GET" && req.method !== "HEAD") return false;
  if (!PUBLIC_HTML_PATHS.some((re) => re.test(req.pathname))) return false;
  // Search results depend on ?q; RSC/prefetch payloads vary on request headers.
  if ((req.search.get("q") ?? "").trim()) return false;
  if (req.search.has("_rsc")) return false;
  if (req.headers.get("rsc") || req.headers.get("next-router-prefetch") || req.headers.get("next-router-state-tree")) {
    return false;
  }
  if (req.headers.get("authorization")) return false;
  // Only real browser page loads (Accept: text/html). curl/RSC fetches stay no-store.
  if (!(req.headers.get("accept") ?? "").includes("text/html")) return false;
  return true;
}

export function htmlCacheHeaders(cacheable: boolean): Record<string, string> {
  if (!cacheable) {
    return {
      "Cache-Control": NO_STORE_VALUE,
      "CDN-Cache-Control": "private, no-store",
      "Vercel-CDN-Cache-Control": "private, no-store",
    };
  }
  const cdn = `public, s-maxage=${HTML_CDN_MAX_AGE_S}, stale-while-revalidate=${HTML_STALE_WHILE_REVALIDATE_S}`;
  return {
    // Browsers always revalidate, so a Boss save shows on next CDN refresh.
    "Cache-Control": "public, max-age=0, must-revalidate",
    // Belt-and-braces: never let the CDN hand an RSC payload to a page load.
    Vary: "RSC, Next-Router-State-Tree, Next-Router-Prefetch, Next-Router-Segment-Prefetch, Accept",
    "CDN-Cache-Control": cdn,
    "Vercel-CDN-Cache-Control": cdn,
  };
}

/** Small TTL memo with explicit invalidation. Failed loads are not cached. */
export function createTtlMemo<T>(ttlMs: number, now: () => number = Date.now) {
  let value: { at: number; data: T } | null = null;
  let inflight: Promise<T> | null = null;
  let generation = 0;
  return {
    async get(load: () => Promise<T>): Promise<T> {
      if (value && now() - value.at < ttlMs) return value.data;
      if (inflight) return inflight;
      const gen = generation;
      inflight = load()
        .then((data) => {
          if (gen === generation) value = { at: now(), data };
          return data;
        })
        .finally(() => {
          inflight = null;
        });
      return inflight;
    },
    clear(): void {
      generation += 1;
      value = null;
      inflight = null;
    },
  };
}
