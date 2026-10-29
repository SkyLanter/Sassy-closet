import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { INTAKE_DIRECT_LINK_HEADERS, INTAKE_DIRECT_LINK_SOURCES } from "../lib/intake-direct-link-headers";

test("direct-link header config covers submissions, export, and ma only", async () => {
  assert.equal(INTAKE_DIRECT_LINK_HEADERS["X-Robots-Tag"], "noindex, nofollow");
  assert.match(INTAKE_DIRECT_LINK_HEADERS["Cache-Control"] ?? "", /no-store/);
  assert.deepEqual(INTAKE_DIRECT_LINK_SOURCES, [
    "/api/submissions",
    "/api/submissions/:path*",
    "/api/export",
    "/api/export/:path*",
    "/api/ma/:path*",
  ]);
  const config = (await import("../next.config")).default;
  assert.equal(typeof config.headers, "function");
  const rules = await config.headers();
  assert.deepEqual(
    rules.map((rule) => rule.source),
    [...INTAKE_DIRECT_LINK_SOURCES],
  );
  for (const rule of rules) {
    const robots = rule.headers.find((header) => header.key === "X-Robots-Tag");
    assert.equal(robots?.value, "noindex, nofollow");
  }
  assert.equal(rules.some((rule) => rule.source === "/" || rule.source === "/admin"), false);
});

test("direct-link routes are not added to a sitemap or the home nav", () => {
  const root = process.cwd();
  for (const rel of ["app/sitemap.ts", "app/sitemap.js", "public/sitemap.xml"]) {
    assert.equal(fs.existsSync(path.join(root, rel)), false, rel);
  }
  const header = fs.readFileSync(path.join(root, "components/BrandHeader.tsx"), "utf8");
  assert.equal(header.includes("/api/submissions"), false);
  assert.equal(header.includes("/api/export"), false);
  assert.equal(header.includes("/api/ma"), false);
});
