import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { assertLiveCatalogIntegrity } from "../lib/catalog-integrity";
import { maLetter } from "../lib/ma";
import {
  assertHoldPricePairing,
  presentLockedBossPrices,
  publicSafeProduct,
} from "../lib/sell-contract";
import type { CatalogDocument, Product } from "../lib/types";

/** Current Blob catalog USD for the hub ten (2026-09-30 tiered margin). */
const CATALOG_USD = {
  A01: 27,
  A02: 23,
  S01: 39,
  K01: 36,
  H01: 8,
  P01: 5,
  P02: 25,
  P03: 11,
  P04: 10,
  P05: 25,
} as const;

function product(ma: keyof typeof CATALOG_USD, priceUsd: number | null, status: Product["status"] = "available"): Product {
  const type = maLetter(ma);
  if (type === null) {
    throw new Error(`Invalid mã ${ma}`);
  }
  return {
    ma,
    type,
    titleVn: ma,
    titleEn: ma,
    priceUsd,
    qty: 1,
    status,
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

function document(products: Product[]): CatalogDocument {
  return {
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    products,
    settings: { announcementLines: [], facebookPageUrl: "https://m.me/example" },
  };
}

test("seed hub prices match the Blob catalog USD", () => {
  const seed = JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as {
    products: { ma: string; priceUsd: number; status: string }[];
  };
  for (const [ma, priceUsd] of Object.entries(CATALOG_USD)) {
    const row = seed.products.find((item) => item.ma === ma);
    assert.equal(row?.status, "available", ma);
    assert.equal(row?.priceUsd, priceUsd, ma);
  }
});

test("hub Available accepts the catalog USD and a later reprice", () => {
  assert.doesNotThrow(() => assertHoldPricePairing("P05", "available", 25));
  assert.doesNotThrow(() => assertHoldPricePairing("P05", "available", 22));
  assert.doesNotThrow(() => assertHoldPricePairing("A01", "available", 27));
  assert.doesNotThrow(() => assertHoldPricePairing("A03", "available", 50));
  assert.throws(() => assertHoldPricePairing("P05", "available", null), /needs a USD price/);
  assert.throws(() => assertHoldPricePairing("P05", "hold", 25), /cannot have a USD price/);
  const source = readFileSync(path.join(process.cwd(), "lib", "sell-contract.ts"), "utf8");
  assert.equal(source.includes("Boss list"), false);
  assert.equal(source.includes("bossRow"), false);
});

test("shop reads publish catalog USD and do not substitute a lock", () => {
  const rows = Object.entries(CATALOG_USD).map(([ma, priceUsd]) =>
    product(ma as keyof typeof CATALOG_USD, priceUsd),
  );
  const extra: Product = {
    ...product("A01", 27),
    ma: "A03",
    titleEn: "Extra",
    titleVn: "Extra",
    priceUsd: 50,
  };
  const catalog = document([...rows, extra]);
  assert.doesNotThrow(() => assertLiveCatalogIntegrity(catalog.products));

  for (const row of rows) {
    assert.equal(publicSafeProduct(row).priceUsd, row.priceUsd);
  }
  const held = publicSafeProduct({ ...product("A01", 27), status: "hold", priceUsd: 27 });
  assert.equal(held.priceUsd, null);

  const presented = presentLockedBossPrices(catalog);
  for (const [ma, priceUsd] of Object.entries(CATALOG_USD)) {
    assert.equal(presented.products.find((row) => row.ma === ma)?.priceUsd, priceUsd);
  }
  assert.equal(presented.products.find((row) => row.ma === "A03")?.priceUsd, 50);

  const oldLock = document([product("A01", 24), ...rows.slice(1)]);
  assert.equal(publicSafeProduct(oldLock.products[0]!).priceUsd, 24);
  assert.doesNotThrow(() => assertLiveCatalogIntegrity(oldLock.products));

  const store = readFileSync(path.join(process.cwd(), "lib", "catalog-store.ts"), "utf8");
  const writeStart = store.indexOf("export async function writeLiveCatalogDocument");
  const writeEnd = store.indexOf("export async function writeLiveCatalog(");
  const writeBody = store.slice(writeStart, writeEnd);
  assert.equal(writeBody.includes("presentLockedBossPrices"), false);
  assert.equal(store.includes("presentLockedBossPrices(hydrateLiveCatalog"), true);
  const boss = readFileSync(path.join(process.cwd(), "lib", "boss-catalog.ts"), "utf8");
  assert.equal(boss.includes("PREVIOUS_BOSS_PRICE_USD"), false);
  assert.equal(boss.includes("BOSS_PRICE_LIST"), false);
});
