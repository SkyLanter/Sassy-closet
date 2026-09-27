import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { BOSS_PRICE_LIST } from "../lib/boss-catalog";
import { assertLiveCatalogIntegrity } from "../lib/catalog-integrity";
import { maLetter } from "../lib/ma";
import {
  assertHoldPricePairing,
  presentLockedBossPrices,
  publicSafeProduct,
} from "../lib/sell-contract";
import type { CatalogDocument, Product } from "../lib/types";

const NEW_SHIPPING = {
  A01: 25,
  A02: 21,
  S01: 39,
  K01: 36,
  H01: 6,
  P01: 3,
  P02: 24,
  P03: 10,
  P04: 7,
  P05: 23,
} as const;

const PREVIOUS_LOCK = {
  A01: 30,
  A02: 26,
  S01: 45,
  K01: 40,
  H01: 10,
  P01: 8,
  P02: 28,
  P03: 15,
  P04: 12,
  P05: 28,
} as const;

function product(ma: keyof typeof NEW_SHIPPING, priceUsd: number): Product {
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

function document(products: Product[]): CatalogDocument {
  return {
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    products,
    settings: { announcementLines: [], facebookPageUrl: "https://m.me/example" },
  };
}

test("Boss list is the new-shipping price for each locked mã", () => {
  assert.deepEqual(
    BOSS_PRICE_LIST.map((row) => row.ma).sort(),
    Object.keys(NEW_SHIPPING).sort(),
  );
  for (const row of BOSS_PRICE_LIST) {
    assert.equal(row.status, "available");
    assert.equal(row.priceUsd, NEW_SHIPPING[row.ma]);
  }
});

test("seed catalog stores the same locked prices", () => {
  const seed = JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as {
    products: { ma: string; priceUsd: number }[];
  };
  for (const [ma, priceUsd] of Object.entries(NEW_SHIPPING)) {
    const row = seed.products.find((product) => product.ma === ma);
    assert.equal(row?.priceUsd, priceUsd, ma);
  }
});

test("P05 $23 is the Boss price and a different USD is rejected", () => {
  assert.doesNotThrow(() => assertHoldPricePairing("P05", "available", 23));
  assert.throws(() => assertHoldPricePairing("P05", "available", 28), /\$23/);
  assert.throws(() => assertHoldPricePairing("P05", "hold", 23), /cannot have a USD price/);
  const source = readFileSync(path.join(process.cwd(), "lib", "sell-contract.ts"), "utf8");
  assert.equal(source.includes("P05 must never publish $23"), false);
});

test("customer override and live read show Boss USD while a raw stale catalog is still rejected", () => {
  const stale = Object.entries(PREVIOUS_LOCK).map(([ma, priceUsd]) =>
    product(ma as keyof typeof NEW_SHIPPING, priceUsd),
  );
  const extra: Product = {
    ...product("A01", 30),
    ma: "A03",
    titleEn: "Extra",
    titleVn: "Extra",
    priceUsd: 50,
  };
  const staleDoc = document([...stale, extra]);

  assert.throws(() => assertLiveCatalogIntegrity(staleDoc.products), /A01 Available price must be \$25/);
  for (const row of stale) {
    assert.equal(publicSafeProduct(row).priceUsd, NEW_SHIPPING[row.ma as keyof typeof NEW_SHIPPING]);
  }

  const presented = presentLockedBossPrices(staleDoc);
  assert.doesNotThrow(() => assertLiveCatalogIntegrity(presented.products));
  for (const [ma, priceUsd] of Object.entries(NEW_SHIPPING)) {
    assert.equal(presented.products.find((row) => row.ma === ma)?.priceUsd, priceUsd);
  }
  assert.equal(presented.products.find((row) => row.ma === "A03")?.priceUsd, 50);

  const store = readFileSync(path.join(process.cwd(), "lib", "catalog-store.ts"), "utf8");
  const writeStart = store.indexOf("export async function writeLiveCatalogDocument");
  const writeEnd = store.indexOf("export async function writeLiveCatalog(");
  const writeBody = store.slice(writeStart, writeEnd);
  assert.equal(writeBody.includes("presentLockedBossPrices"), false);
  assert.equal(store.includes("presentLockedBossPrices(hydrateLiveCatalog"), true);
});
