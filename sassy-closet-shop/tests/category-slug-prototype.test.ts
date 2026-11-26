import assert from "node:assert/strict";
import test from "node:test";
import { NextRequest } from "next/server";
import { categoryFromSlug } from "../lib/categories";
import { canonicalCategoryPath } from "../lib/ma-url";
import { proxy } from "../proxy";

// The category slug is a customer URL segment. It must only ever resolve a slug
// that this shop wrote. A plain object lookup also answers Object.prototype
// members ("constructor", "__proto__", "toString"), which are not categories.
const PROTOTYPE_KEYS = Object.getOwnPropertyNames(Object.prototype);

function notFoundDigest(error: unknown): string {
  return error && typeof error === "object" && "digest" in error
    ? String((error as { digest?: unknown }).digest)
    : "";
}

test("only a real category slug resolves; Object.prototype names do not", () => {
  assert.equal(categoryFromSlug("ao"), "A");
  assert.equal(categoryFromSlug("phu-kien"), "P");
  assert.equal(categoryFromSlug("tops"), null);
  assert.equal(categoryFromSlug("nope"), null);
  for (const name of PROTOTYPE_KEYS) {
    assert.equal(categoryFromSlug(name), null, `slug ${JSON.stringify(name)}`);
    assert.equal(categoryFromSlug(name.toLowerCase()), null, `slug ${JSON.stringify(name.toLowerCase())}`);
  }
});

test("a non-category slug is never rewritten into a redirect", () => {
  assert.equal(canonicalCategoryPath("/c/ao"), null, "already canonical");
  assert.equal(canonicalCategoryPath("/c/Ao"), "/c/ao", "a real slug lowercases");
  assert.equal(canonicalCategoryPath("/c/phu-kien-toc"), "/c/toc", "the one stale slug redirects");
  assert.equal(canonicalCategoryPath("/c/Tops"), null, "an English word is not a slug");
  for (const name of PROTOTYPE_KEYS) {
    assert.equal(canonicalCategoryPath(`/c/${name}`), null, `path ${JSON.stringify(name)}`);
  }
  for (const pathname of ["/c/constructor", "/c/CONSTRUCTOR", "/c/__proto__", "/c/toString"]) {
    const response = proxy(new NextRequest(`https://shop.example${pathname}`));
    assert.equal(response.headers.get("location"), null, pathname);
    assert.notEqual(response.status, 308, pathname);
  }
});

test("a category page with a prototype-name slug is a 404, not a crash", async () => {
  const page = await import("../app/(shop)/c/[slug]/page");
  for (const slug of ["constructor", "__proto__", "toString", "hasOwnProperty"]) {
    await assert.rejects(
      () => page.default({ params: Promise.resolve({ slug }) }),
      (error: unknown) => {
        assert.equal(notFoundDigest(error), "NEXT_HTTP_ERROR_FALLBACK;404", `slug ${slug}`);
        return true;
      },
    );
  }
});
