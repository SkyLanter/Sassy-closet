import assert from "node:assert/strict";
import test from "node:test";
import { NextRequest } from "next/server";
import { HELD_INCOMPLETE_MAS, NEVER_LIST_MAS } from "../lib/held-incomplete";
import { PRIVATE_NOT_FOUND_HEADERS } from "../lib/private-robots";
import { notFoundSeo, rootSeo } from "../lib/seo";
import { proxy } from "../proxy";

const ROBOTS_HEADER = /noindex,\s*nofollow,\s*nosnippet/i;

/**
 * Next merges child metadata over the root layout. `robots: null` becomes
 * no robots tag, so a 404 (unknown mã, held mã, unknown category) drops
 * the shop noindex. Held and missing pages must stay noindex even after
 * the shop is allowed to be indexed.
 */
function robotsIndex(robots: unknown): boolean | undefined {
  if (!robots || typeof robots !== "object" || !("index" in robots)) {
    return undefined;
  }
  const index = (robots as { index?: unknown }).index;
  return typeof index === "boolean" ? index : undefined;
}

test("plain 404s for held photos and share cards stay noindex", () => {
  assert.equal(PRIVATE_NOT_FOUND_HEADERS["X-Robots-Tag"], "noindex, nofollow, nosnippet");
  assert.match(PRIVATE_NOT_FOUND_HEADERS["Cache-Control"], /no-store/);
});

test("not-found metadata stays noindex and does not clear the root robots tag", () => {
  const missing = notFoundSeo();
  assert.equal(robotsIndex(missing.robots), false);
  assert.equal(
    missing.robots && typeof missing.robots === "object" && "follow" in missing.robots
      ? (missing.robots as { follow?: unknown }).follow
      : undefined,
    false,
  );
  assert.equal(
    missing.robots && typeof missing.robots === "object" && "nosnippet" in missing.robots
      ? (missing.robots as { nosnippet?: unknown }).nosnippet
      : undefined,
    true,
  );
  assert.deepEqual(missing.alternates, { canonical: null });
  assert.notEqual(missing.robots, null);
});

test("held and unknown shop HTML paths send X-Robots-Tag and live priced mãs do not", () => {
  const savedMode = process.env.SITE_MODE;
  const savedPublic = process.env.NEXT_PUBLIC_SITE_MODE;
  process.env.SITE_MODE = "official";
  process.env.NEXT_PUBLIC_SITE_MODE = "official";
  try {
    const missing = ["/m/NOPE", "/m/Z01", "/c/not-a-real-slug", "/c/NOPE"];
    for (const ma of [...HELD_INCOMPLETE_MAS, ...NEVER_LIST_MAS]) {
      missing.push(`/m/${ma}`);
    }
    for (const path of missing) {
      const response = proxy(new NextRequest(`http://127.0.0.1${path}`));
      // Proxy continues. The page calls notFound(); this header is copied onto that 404.
      assert.equal(response.status, 200, path);
      assert.match(response.headers.get("x-robots-tag") ?? "", ROBOTS_HEADER, path);
    }
    // Priced looks stay unmarked. A well-formed miss such as /m/S99 is unmarked too:
    // this seed omits S06, so "not in the seed" is not a 404 signal.
    for (const path of ["/m/S03", "/m/S06", "/m/S99", "/m/A01", "/c/ao", "/c/set", "/"]) {
      const response = proxy(new NextRequest(`http://127.0.0.1${path}`));
      assert.equal(response.headers.get("x-robots-tag"), null, path);
    }
    const redirect = proxy(new NextRequest("http://127.0.0.1/m/s14"));
    assert.equal(redirect.status, 308);
    assert.equal(redirect.headers.get("x-robots-tag"), null);
  } finally {
    if (savedMode === undefined) delete process.env.SITE_MODE;
    else process.env.SITE_MODE = savedMode;
    if (savedPublic === undefined) delete process.env.NEXT_PUBLIC_SITE_MODE;
    else process.env.NEXT_PUBLIC_SITE_MODE = savedPublic;
  }
});

test("held and missing pages stay noindex when the shop itself is official", () => {
  const savedMode = process.env.SITE_MODE;
  const savedPublic = process.env.NEXT_PUBLIC_SITE_MODE;
  process.env.SITE_MODE = "official";
  process.env.NEXT_PUBLIC_SITE_MODE = "official";
  try {
    assert.equal(robotsIndex(rootSeo().robots), true);
    assert.equal(robotsIndex(notFoundSeo().robots), false);
  } finally {
    if (savedMode === undefined) delete process.env.SITE_MODE;
    else process.env.SITE_MODE = savedMode;
    if (savedPublic === undefined) delete process.env.NEXT_PUBLIC_SITE_MODE;
    else process.env.NEXT_PUBLIC_SITE_MODE = savedPublic;
  }
});
