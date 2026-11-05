import assert from "node:assert/strict";
import { createRequire } from "node:module";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { NextRequest } from "next/server";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { config, proxy } from "../proxy";

type MiddlewareMatcher = { regexp: string };

type GetMiddlewareMatchers = (
  matcher: readonly string[],
  nextConfig: { basePath?: string },
) => MiddlewareMatcher[];

type GetMiddlewareRouteMatcher = (
  matchers: readonly MiddlewareMatcher[],
) => (pathname: string) => boolean;

const nodeRequire = createRequire(import.meta.url);
const { getMiddlewareMatchers } = nodeRequire("next/dist/build/analysis/get-page-static-info") as {
  getMiddlewareMatchers: GetMiddlewareMatchers;
};
const { getMiddlewareRouteMatcher } = nodeRequire(
  "next/dist/shared/lib/router/utils/middleware-route-matcher",
) as {
  getMiddlewareRouteMatcher: GetMiddlewareRouteMatcher;
};

const matchesProxy = getMiddlewareRouteMatcher(getMiddlewareMatchers([...config.matcher], {}));

const held = HELD_INCOMPLETE_MAS[0]!;

/** Each folder character as %HH. encodeURIComponent leaves ASCII letters and digits alone. */
function percentFolder(folder: string): string {
  return [...folder]
    .map((char) => `%${char.charCodeAt(0).toString(16).padStart(2, "0").toUpperCase()}`)
    .join("");
}

function get(pathname: string): Response {
  return proxy(new NextRequest(`http://127.0.0.1${pathname}`, { method: "GET" }));
}

async function assertOffLiveImage(pathname: string): Promise<void> {
  const response = get(pathname);
  assert.equal(response.status, 404, pathname);
  assert.equal(await response.text(), "Not found", pathname);
  assert.match(response.headers.get("cache-control") ?? "", /no-store/, pathname);
  assert.equal(response.headers.get("location"), null, pathname);
}

test("proxy 404s a held product image before any redirect", async () => {
  await assertOffLiveImage(`/products/${held}/cover.jpg`);
  await assertOffLiveImage(`/products/${held.toLowerCase()}/cover.jpg`);
  await assertOffLiveImage(`/products/${held[0] + "0" + held.slice(1)}/cover.jpg`);
  await assertOffLiveImage(`/products/${percentFolder(held)}/cover.jpg`);
  await assertOffLiveImage(`/products/A01/../${held}/cover.jpg`);
  await assertOffLiveImage(`/products/${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/products/${held}%2fcover.jpg`);
  await assertOffLiveImage(`/products%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/products%2F${held}/cover.jpg`);
  await assertOffLiveImage(`/products%2f${held}%2fcover.jpg`);
  await assertOffLiveImage(`/products%2F${held.toLowerCase()}%2Fcover.jpg`);
  await assertOffLiveImage(`/products%2F${held[0] + "0" + held.slice(1)}%2Fcover.jpg`);
  await assertOffLiveImage(`/products%2F${held}%2Fcover.jpg/`);
  await assertOffLiveImage(`/products%2F${held}%2Fcover.jpg?w=640`);
  await assertOffLiveImage(`/%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/%2fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/%2F%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/%2E%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/.%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/%2e%2fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/%2E%2F%2E%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/foo%2F..%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/foo%2F%2E%2E%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/foo%2F.%2F..%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/foo%2F..%2F.%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/a%2F..%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/foo%2Fbar%2F..%2F..%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/products%2F..%2Fproducts%2F${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/foo%2F..%2Fproducts%2FA24%2Fcover.jpg`);
  await assertOffLiveImage(`/%2Fproducts%2FA24%2Fphoto-2.jpg`);
});

test("proxy 308s a short live product image spelling to the canonical folder", () => {
  const response = get("/products/a1/cover.jpg");
  assert.equal(response.status, 308);
  const location = response.headers.get("location");
  assert.ok(location);
  assert.equal(new URL(location, "http://127.0.0.1").pathname, "/products/A01/cover.jpg");
});

test("canonical live images and held product pages are not the image 404", () => {
  for (const pathname of [
    "/products/A01/cover.jpg",
    "/products/S06/cover.jpg",
    `/m/${held}`,
    "/products%2FA01%2Fcover.jpg",
    "/products%2FS06%2Fcover.jpg",
    "/products%2Fa1%2Fcover.jpg",
    `/products%252F${held}%252Fcover.jpg`,
    `/m%2F${held}`,
    `/foo%2Fproducts%2F${held}%2Fcover.jpg`,
    `/foo%2F..%2Fproducts%2FA01%2Fcover.jpg`,
    `/foo%2F..%2Fproducts%2FS06%2Fcover.jpg`,
    `/%2Fproducts%2FA01%2Fcover.jpg`,
    `/%2E%2Fproducts%2FS06%2Fcover.jpg`,
    `/..%2Fproducts%2F${held}%2Fcover.jpg`,
    `/foo%2F..%2F..%2Fproducts%2F${held}%2Fcover.jpg`,
  ]) {
    const response = get(pathname);
    assert.notEqual(response.status, 404, pathname);
    assert.notEqual(response.status, 308, pathname);
  }
});

function publicDirParts(): string[] {
  const publicDir = path.posix.join(process.cwd().replaceAll("\\", "/"), "public");
  return publicDir.split("/").filter((segment) => segment.length > 0);
}

/** One decode plus the dev public-dir join. `ups` pops `foo` and the public root. */
function walkBackToPublic(folder: string, parts = publicDirParts()): string {
  const ups = Array.from({ length: parts.length + 1 }, () => "..").join("%2F");
  const restored = parts.map((segment) => encodeURIComponent(segment)).join("%2F");
  return `/foo%2F${ups}%2F${restored}%2Fproducts%2F${encodeURIComponent(folder)}%2Fcover.jpg`;
}

test("a path that walks back through public still 404s the held file", async () => {
  assert.equal(path.basename(process.cwd()), "sassy-closet-shop");
  const pathnames = [
    `/foo%2F..%2F..%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`,
    `/foo%2F%2E%2E%2F%2E%2E%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`,
    `/uploads/..%2F..%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`,
    `/..%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`,
    `/uploads/foo/..%2F..%2F..%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`,
    `/foo%2F..%2F..%2F..%2Fsassy-closet-shop%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`,
    `/uploads/..%2F..%2F..%2Fsassy-closet-shop%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`,
    `/foo%2F%2E%2E%2F%2E%2E%2F%2E%2E%2Fsassy-closet-shop%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`,
    walkBackToPublic(held),
  ];
  for (const pathname of pathnames) {
    assert.equal(matchesProxy(pathname), true, pathname);
    await assertOffLiveImage(pathname);
  }
  for (const pathname of [
    `/foo%2F..%2F..%2Fpublic%2Fproducts%2FA01%2Fcover.jpg`,
    `/foo%2F..%2F..%2Fpublic%2Fproducts%2FS06%2Fcover.jpg`,
    `/uploads/..%2F..%2Fpublic%2Fproducts%2FS06%2Fcover.jpg`,
    `/foo%2F..%2F..%2Fpublic%2Ffoo%2Fproducts%2F${held}%2Fcover.jpg`,
    `/foo%2F..%2F..%2F..%2Fsassy-closet-shop%2Fpublic%2Fproducts%2FA01%2Fcover.jpg`,
    `/foo%2F..%2F..%2F..%2Fsassy-closet-shop%2Fpublic%2Fproducts%2FS06%2Fcover.jpg`,
    `/uploads/..%2F..%2F..%2Fsassy-closet-shop%2Fpublic%2Fproducts%2FS06%2Fcover.jpg`,
    `/foo%2F..%2F..%2F..%2Fother-shop%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`,
    walkBackToPublic(held, publicDirParts().map((segment, index, parts) => (index === parts.length - 3 ? "not-this-checkout" : segment))),
    walkBackToPublic("A01"),
    walkBackToPublic("S06"),
  ]) {
    const response = get(pathname);
    assert.notEqual(response.status, 404, pathname);
  }
});

test("a shop-directory walk still 404s when the process started above the shop", async () => {
  const shopDir = path.posix.dirname(path.posix.dirname(fileURLToPath(import.meta.url)));
  const previous = process.cwd();
  process.chdir(path.posix.dirname(shopDir));
  try {
    assert.notEqual(path.basename(process.cwd()), "sassy-closet-shop");
    const shopName = path.posix.basename(shopDir);
    const heldPath = `/foo%2F..%2F..%2F..%2F${shopName}%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`;
    const uploadsPath = `/uploads/..%2F..%2F..%2F${shopName}%2Fpublic%2Fproducts%2F${held}%2Fcover.jpg`;
    assert.equal(matchesProxy(heldPath), true);
    assert.equal(matchesProxy(uploadsPath), true);
    await assertOffLiveImage(heldPath);
    await assertOffLiveImage(uploadsPath);
    const live = get(`/foo%2F..%2F..%2F..%2F${shopName}%2Fpublic%2Fproducts%2FS06%2Fcover.jpg`);
    assert.notEqual(live.status, 404);
    const canonical = get("/products/a1/cover.jpg");
    assert.equal(canonical.status, 308);
  } finally {
    process.chdir(previous);
  }
});

test("a dot segment under a skipped static prefix still 404s the held file", async () => {
  const pathnames = [
    `/uploads/..%2Fproducts/${held}/cover.jpg`,
    `/uploads/..%2fproducts/${held}/cover.jpg`,
    `/uploads/%2E%2E%2Fproducts%2F${held}%2Fcover.jpg`,
    `/uploads/%2e%2e%2fproducts%2f${held}%2fcover.jpg`,
    `/uploads/.%2E%2Fproducts/${held}/cover.jpg`,
    `/uploads/%2E.%2Fproducts/${held}/cover.jpg`,
    `/uploads/foo/..%2F..%2Fproducts/${held}/cover.jpg`,
    "/uploads/..%2Fproducts/A24/photo-2.jpg",
    `/editorial/..%2Fproducts/${held}/cover.jpg`,
    "/editorial/..%2Fproducts/A24/photo-2.jpg",
    `/favicon.ico/..%2Fproducts/${held}/cover.jpg`,
    `/favicon.ico%2F..%2Fproducts%2F${held}%2Fcover.jpg`,
    `/icon.svg/..%2Fproducts/${held}/cover.jpg`,
    `/icon.svg%2F..%2Fproducts%2F${held}%2Fcover.jpg`,
    `/_next/static/..%2F..%2Fproducts/${held}/cover.jpg`,
    `/_next/static%2F..%2F..%2Fproducts%2F${held}%2Fcover.jpg`,
    "/_next/static/..%2F..%2Fproducts/A24/photo-2.jpg",
    `/_next/image/..%2F..%2Fproducts/${held}/cover.jpg`,
    `/_next/image%2F..%2F..%2Fproducts%2F${held}%2Fcover.jpg`,
  ];
  for (const pathname of pathnames) {
    assert.equal(matchesProxy(pathname), true, pathname);
    await assertOffLiveImage(pathname);
  }
});

test("plain static files stay outside the proxy", () => {
  for (const pathname of [
    "/favicon.ico",
    "/icon.svg",
    "/_next/static/chunks/main.js",
    "/_next/image",
    "/uploads/photo.jpg",
    "/uploads/foo%2Ejpg",
    "/editorial/hero.jpg",
  ]) {
    assert.equal(matchesProxy(pathname), false, pathname);
  }
});

test("a dot segment under a skipped prefix does not 404 a live folder", () => {
  for (const pathname of [
    "/uploads/..%2Fproducts/S06/cover.jpg",
    "/uploads/..%2Fproducts/A01/cover.jpg",
    "/editorial/..%2Fproducts/a1/cover.jpg",
  ]) {
    assert.equal(matchesProxy(pathname), true, pathname);
    const response = get(pathname);
    assert.notEqual(response.status, 404, pathname);
  }
});

test("a malformed product image percent-escape does not throw and is not the off-live 404", () => {
  for (const pathname of ["/products/%E0%A4%A/cover.jpg", "/products%2F%E0%A4%A"]) {
    let response: Response | undefined;
    assert.doesNotThrow(() => {
      response = get(pathname);
    });
    assert.ok(response);
    assert.notEqual(response.status, 404, pathname);
  }
});
