import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import {
  CATALOG_MEMO_TTL_MS,
  createTtlMemo,
  htmlCacheHeaders,
  isCdnCacheableHtml,
  productImageCacheHeaders,
} from "../lib/cache-policy";

function req(pathname: string, query = "", headers: Record<string, string> = {}, method = "GET") {
  const all = { Accept: "text/html,application/xhtml+xml", ...headers };
  const lower = Object.fromEntries(Object.entries(all).map(([k, v]) => [k.toLowerCase(), v]));
  return {
    method,
    pathname,
    search: new URLSearchParams(query),
    headers: { get: (name: string) => lower[name.toLowerCase()] ?? null },
  };
}

test("public shop pages are CDN-cacheable", () => {
  for (const p of ["/", "/m/A01", "/c/ao", "/how-to-buy", "/meetup-ship"]) {
    assert.equal(isCdnCacheableHtml(req(p)), true, p);
  }
});

test("admin, api, search, RSC and non-GET are never CDN-cached", () => {
  assert.equal(isCdnCacheableHtml(req("/admin")), false);
  assert.equal(isCdnCacheableHtml(req("/admin/edit/A01")), false);
  assert.equal(isCdnCacheableHtml(req("/api/admin/save")), false);
  assert.equal(isCdnCacheableHtml(req("/api/health")), false);
  assert.equal(isCdnCacheableHtml(req("/", "q=dress")), false);
  assert.equal(isCdnCacheableHtml(req("/m/A01", "_rsc=abc")), false);
  assert.equal(isCdnCacheableHtml(req("/m/A01", "", { RSC: "1" })), false);
  assert.equal(isCdnCacheableHtml(req("/m/A01", "", { "Next-Router-Prefetch": "1" })), false);
  assert.equal(isCdnCacheableHtml(req("/m/A01", "", {}, "POST")), false);
  assert.equal(isCdnCacheableHtml(req("/m/A01", "", { Authorization: "Basic x" })), false);
  assert.equal(isCdnCacheableHtml(req("/m/A01", "", { Accept: "*/*" })), false);
});

test("html headers: browser always revalidates, CDN 60s + swr 300s", () => {
  const on = htmlCacheHeaders(true);
  assert.equal(on["Cache-Control"], "public, max-age=0, must-revalidate");
  assert.equal(on["Vercel-CDN-Cache-Control"], "public, s-maxage=60, stale-while-revalidate=300");
  assert.match(on.Vary, /RSC/);
  assert.match(on.Vary, /Accept/);
  const off = htmlCacheHeaders(false);
  assert.match(off["Cache-Control"], /no-store/);
  assert.match(off["Vercel-CDN-Cache-Control"], /no-store/);
});

test("product photo headers are public and CDN-cached", () => {
  const h = productImageCacheHeaders();
  assert.match(h["Cache-Control"], /^public, max-age=3600, s-maxage=86400/);
  assert.match(h["Vercel-CDN-Cache-Control"], /s-maxage=86400, stale-while-revalidate=604800/);
});

test("ttl memo: one load within TTL, reload after TTL, clear forces reload", async () => {
  let t = 0;
  let loads = 0;
  const memo = createTtlMemo<number>(CATALOG_MEMO_TTL_MS, () => t);
  const load = async () => ++loads;
  assert.equal(await memo.get(load), 1);
  t = CATALOG_MEMO_TTL_MS - 1;
  assert.equal(await memo.get(load), 1);
  t = CATALOG_MEMO_TTL_MS;
  assert.equal(await memo.get(load), 2);
  memo.clear();
  assert.equal(await memo.get(load), 3);
});

/** A load the test resolves by hand: no timers, so box load cannot reorder anything. */
function deferredLoad(): { load: () => Promise<number>; resolve: (v: number) => void; calls: () => number } {
  let calls = 0;
  let resolvers: ((v: number) => void)[] = [];
  return {
    load: () => {
      calls += 1;
      return new Promise<number>((r) => resolvers.push(r));
    },
    resolve: (v) => {
      for (const r of resolvers) r(v);
      resolvers = [];
    },
    calls: () => calls,
  };
}

test("ttl memo: concurrent reads share one load; failures are not cached", async () => {
  let t = 0;
  const memo = createTtlMemo<number>(CATALOG_MEMO_TTL_MS, () => t);
  const first = deferredLoad();
  const pair = Promise.all([memo.get(first.load), memo.get(first.load)]);
  assert.equal(first.calls(), 1);
  first.resolve(1);
  assert.deepEqual(await pair, [1, 1]);
  t = CATALOG_MEMO_TTL_MS - 1;
  assert.equal(await memo.get(first.load), 1);
  assert.equal(first.calls(), 1, "served from cache inside the lifetime");

  t = CATALOG_MEMO_TTL_MS;
  const second = deferredLoad();
  const herd = Promise.all([memo.get(second.load), memo.get(second.load), memo.get(second.load)]);
  assert.equal(second.calls(), 1, "expired entry refetched exactly once");
  second.resolve(2);
  assert.deepEqual(await herd, [2, 2, 2]);

  const failing = createTtlMemo<number>(CATALOG_MEMO_TTL_MS, () => t);
  await assert.rejects(failing.get(async () => { throw new Error("blob down"); }));
  assert.equal(await failing.get(async () => 7), 7);
});

test("ttl memo: clear during an in-flight load does not cache the stale result", async () => {
  const t = 0;
  const memo = createTtlMemo<number>(CATALOG_MEMO_TTL_MS, () => t);
  const stale = deferredLoad();
  const pending = memo.get(stale.load);
  memo.clear();
  stale.resolve(1);
  assert.equal(await pending, 1);
  assert.equal(await memo.get(async () => 99), 99);
});

test("wiring: writes + refreshShop clear the memo; admin reads stay fresh", () => {
  const store = readFileSync(new URL("../lib/catalog-store.ts", import.meta.url), "utf8");
  assert.match(store, /writeLiveCatalogDocument\(document: CatalogDocument\)[^{]*\{\n  invalidateLiveCatalogMemo\(\);/);
  assert.match(store, /export async function readLiveCatalogRecord\(\)[^{]*\{\n  return readLiveCatalogRecordFresh\(\);/);
  const refresh = readFileSync(new URL("../lib/refresh-shop.ts", import.meta.url), "utf8");
  assert.match(refresh, /function markShopStale[^{]*\{\n  invalidateLiveCatalogMemo\(\);/);
  const products = readFileSync(new URL("../lib/products.ts", import.meta.url), "utf8");
  assert.match(products, /getCatalogDocumentUncached\(\)[^{]*\{\n  return loadRequestCatalog\(\);/);
  for (const admin of ["save", "rename"]) {
    const src = readFileSync(new URL(`../app/api/admin/${admin}/route.ts`, import.meta.url), "utf8");
    assert.doesNotMatch(src, /ForShop/, admin);
  }
});

test("wiring: photo 404s stay no-store; admin keeps next.config no-store", () => {
  const route = readFileSync(new URL("../app/products/[ma]/[file]/route.ts", import.meta.url), "utf8");
  assert.match(route, /status: 404, headers: NO_STORE_HEADERS/);
  assert.match(route, /!isSellableMa\(ma\)/);
  const cfg = readFileSync(new URL("../next.config.ts", import.meta.url), "utf8");
  assert.match(cfg, /source: "\/admin\/:path\*", headers: privateSurface/);
  assert.match(cfg, /source: "\/api\/:path\*", headers: privateSurface/);
  assert.match(cfg, /X-Robots-Tag", value: PRIVATE_ROBOTS_TAG/);
  const robots = readFileSync(new URL("../lib/private-robots.ts", import.meta.url), "utf8");
  assert.match(robots, /noindex, nofollow, nosnippet/);
});
