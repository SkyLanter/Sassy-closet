import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { NextRequest } from "next/server";
import { emptyFitCm } from "../lib/asia-size";
import { HELD_INCOMPLETE_MAS, NEVER_LIST_MAS, isOffLiveSell } from "../lib/held-incomplete";
import { maLetter } from "../lib/ma";
import { findShopProduct } from "../lib/products";
import { isShopPrivateSurface } from "../lib/private-robots";
import { s06PriceLockError } from "../lib/sell-contract";
import { publicShopHealth, shopHealthError } from "../lib/shop-health";
import { shopVisibleProducts } from "../lib/site-settings";
import type { Product } from "../lib/types";
import { proxy } from "../proxy";
import robots from "../app/robots";
import { wouldBeLiveUsd } from "../../shared/tiered-pricing";

function product(ma: string): Product {
  const type = maLetter(ma);
  if (type === null) {
    throw new Error(`Invalid mã ${ma}`);
  }
  return {
    ma,
    type,
    titleVn: ma,
    titleEn: ma,
    priceUsd: 25,
    qty: 1,
    status: "available",
    colors: [],
    images: [],
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

function walk(dir: string, acc: string[]): void {
  for (const name of readdirSync(dir)) {
    const full = path.join(dir, name);
    if (statSync(full).isDirectory()) {
      walk(full, acc);
      continue;
    }
    if (name.endsWith(".tsx")) {
      acc.push(full);
    }
  }
}

test("shop api and admin are noindex, disallowed, and out of sitemap and nav", () => {
  for (const pathname of ["/api/health", "/api/admin/revalidate", "/admin", "/admin/new"]) {
    assert.equal(isShopPrivateSurface(pathname), true, pathname);
  }
  assert.equal(isShopPrivateSurface("/"), false);
  assert.equal(isShopPrivateSurface("/m/S06"), false);
  const rules = robots();
  const rule = Array.isArray(rules.rules) ? rules.rules[0] : rules.rules;
  const disallow = JSON.stringify(rule?.disallow ?? "");
  assert.match(disallow, /\/admin/);
  assert.match(disallow, /\/api/);
  assert.notEqual(rule?.disallow, "/");
  const sitemap = readFileSync(path.join(process.cwd(), "app/sitemap.ts"), "utf8");
  assert.equal(sitemap.includes("/admin"), false);
  assert.equal(sitemap.includes("/api"), false);
  assert.match(sitemap, /shopVisibleProducts/);
  const header = readFileSync(path.join(process.cwd(), "components/header.tsx"), "utf8");
  assert.equal(header.includes("/admin"), false);
  assert.equal(header.includes("/api/"), false);
  const files: string[] = [];
  walk(path.join(process.cwd(), "app"), files);
  walk(path.join(process.cwd(), "components"), files);
  for (const file of files) {
    const text = readFileSync(file, "utf8");
    assert.equal(/type\s*=\s*["']password["']/.test(text), false, file);
  }
});

test("proxy noindex covers api and admin and not the lookbook", () => {
  const health = proxy(new NextRequest("http://127.0.0.1/api/health"));
  assert.notEqual(health.status, 404);
  assert.match(health.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
  const admin = proxy(new NextRequest("http://127.0.0.1/admin"));
  assert.equal(admin.status, 404);
  assert.match(admin.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
  const home = proxy(new NextRequest("http://127.0.0.1/"));
  assert.equal(home.headers.get("x-robots-tag"), null);
  const product = proxy(new NextRequest("http://127.0.0.1/m/A01"));
  assert.equal(product.headers.get("x-robots-tag"), null);
});

test("S06 quote stays $25 across spellings and other short mãs stay invalid", () => {
  for (const ma of ["S06", "S6", "s006", " S006 "]) {
    const locked = wouldBeLiveUsd({
      ma,
      kind: "S",
      liveUsd: 30,
      costCny: null,
      costUsd: null,
    });
    assert.equal(locked.ma, "S06", ma);
    assert.equal(locked.wouldBeUsd, 25, ma);
    assert.equal(locked.reason, "locked", ma);
    assert.equal(s06PriceLockError(ma, 30), "Import rejected S06 price. S06 stays $25.", ma);
    assert.equal(s06PriceLockError(ma, 25), null, ma);
  }
  assert.equal(s06PriceLockError("A01", 27), null);
  assert.throws(
    () =>
      wouldBeLiveUsd({
        ma: "A1",
        kind: "A",
        liveUsd: 27,
        costCny: null,
        costUsd: null,
      }),
    /invalid/,
  );
});

test("held and never-list spellings stay off the public list", () => {
  const held = HELD_INCOMPLETE_MAS[0];
  assert.ok(held);
  const padded = `${held[0]}0${held.slice(1)}`;
  const visible = shopVisibleProducts([
    product(held),
    product(padded),
    product(padded.toLowerCase()),
    product("S06"),
    product("A01"),
  ]);
  assert.deepEqual(
    visible.map((item) => item.ma),
    ["S06", "A01"],
  );
  assert.equal(findShopProduct(visible, "s006")?.priceUsd, 25);
  assert.equal(findShopProduct(visible, "S6")?.ma, "S06");
  assert.equal(findShopProduct(visible, padded), undefined);
  assert.equal(findShopProduct(visible, held.toLowerCase()), undefined);
  for (const ma of HELD_INCOMPLETE_MAS) {
    assert.equal(isOffLiveSell(ma.toLowerCase()), true, ma);
    assert.equal(isOffLiveSell(`${ma[0]}0${ma.slice(1)}`), true, ma);
  }
  for (const ma of NEVER_LIST_MAS) {
    assert.equal(shopVisibleProducts([product(ma)]).length, 0, ma);
  }
});

test("public shop health names blob versus seed and drops layout secrets", async () => {
  const shaped = publicShopHealth({
    ok: true,
    schema: "catalog.v1",
    reading: "seed",
    blobConfigured: false,
    blobReadable: false,
    productCount: 1,
    shopVisible: 1,
    hubMessageReady: 1,
    missingKnown: [],
    knownMas: ["A01"],
  });
  assert.deepEqual(Object.keys(shaped.blob).sort(), ["configured", "readable"]);
  assert.equal(shaped.reading, "seed");
  assert.deepEqual(shopHealthError(true), { ok: false, error: "Catalog read failed", corrupt: true });
  const route = readFileSync(path.join(process.cwd(), "app/api/health/route.ts"), "utf8");
  assert.equal(route.includes("error.message"), false);
  assert.equal(route.includes("blob.listed"), false);
  assert.equal(route.includes("blob.path"), false);
  assert.equal(route.includes("blob.prefix"), false);

  const saved: Record<string, string | undefined> = {};
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL|TOKEN|SECRET/i.test(key)) {
      saved[key] = process.env[key];
      delete process.env[key];
    }
  }
  try {
    const { GET } = await import("../app/api/health/route");
    const response = await GET();
    assert.notEqual(response.status, 401);
    assert.match(response.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
    const body = (await response.json()) as {
      reading?: string;
      blob?: Record<string, unknown>;
      error?: string;
    };
    assert.equal(body.reading, "seed");
    assert.deepEqual(body.blob && Object.keys(body.blob).sort(), ["configured", "readable"]);
    assert.equal(body.blob?.readable, false);
    const text = JSON.stringify(body);
    assert.equal(text.includes("token"), false);
    assert.equal(text.includes("listed"), false);
    assert.equal(text.includes("@"), false);
  } finally {
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
  }
});
