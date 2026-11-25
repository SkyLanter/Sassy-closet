import assert from "node:assert/strict";
import test from "node:test";
import { PRIVATE_NOT_FOUND_HEADERS } from "../lib/private-robots";
import { notFoundSeo, rootSeo } from "../lib/seo";

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
