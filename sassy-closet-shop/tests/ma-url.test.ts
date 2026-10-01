import assert from "node:assert/strict";
import test from "node:test";
import { NextRequest } from "next/server";
import { canonicalCategoryPath, canonicalMaPath } from "../lib/ma-url";
import { proxy } from "../proxy";

test("mã paths canonicalize case and leave canonical paths alone", () => {
  assert.equal(canonicalMaPath("/m/a01"), "/m/A01");
  assert.equal(canonicalMaPath("/m/A01"), null);
  assert.equal(canonicalMaPath("/m/a01/opengraph-image"), "/m/A01/opengraph-image");
  assert.equal(canonicalMaPath("/share/m/a01"), "/share/m/A01");
  assert.equal(canonicalMaPath("/c/ao"), null);
});

test("stale hair slug redirects to toc and accessories stay put", () => {
  assert.equal(canonicalCategoryPath("/c/phu-kien-toc"), "/c/toc");
  assert.equal(canonicalCategoryPath("/c/Phu-Kien-Toc"), "/c/toc");
  assert.equal(canonicalCategoryPath("/c/phu-kien-toc/"), "/c/toc");
  assert.equal(canonicalCategoryPath("/share/c/phu-kien-toc"), "/share/c/toc");
  assert.equal(canonicalCategoryPath("/c/toc"), null);
  assert.equal(canonicalCategoryPath("/c/phu-kien"), null);
  assert.equal(canonicalCategoryPath("/c/Ao"), "/c/ao");
  assert.equal(canonicalCategoryPath("/share/c/Ao"), "/share/c/ao");
  assert.equal(canonicalCategoryPath("/c/tops"), null);
});

/** Next rewrites the request host, so compare path and query only. */
function redirectTarget(response: Response): URL {
  const location = response.headers.get("location");
  assert.ok(location);
  return new URL(location);
}

test("proxy 308s the stale hair path and keeps the query", () => {
  const hair = proxy(new NextRequest("http://127.0.0.1/c/phu-kien-toc?q=clip"));
  assert.equal(hair.status, 308);
  const hairUrl = redirectTarget(hair);
  assert.equal(hairUrl.pathname, "/c/toc");
  assert.equal(hairUrl.search, "?q=clip");

  const share = proxy(new NextRequest("http://127.0.0.1/share/c/phu-kien-toc"));
  assert.equal(share.status, 308);
  assert.equal(redirectTarget(share).pathname, "/share/c/toc");

  const accessories = proxy(new NextRequest("http://127.0.0.1/c/phu-kien"));
  assert.notEqual(accessories.status, 308);
  const current = proxy(new NextRequest("http://127.0.0.1/c/toc"));
  assert.notEqual(current.status, 308);
});
