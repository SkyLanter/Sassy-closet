import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { productFromFields, saveProductInCatalog } from "../lib/admin-ops";
import { emptyFitCm } from "../lib/asia-size";
import { assertLiveCatalogIntegrity } from "../lib/catalog-integrity";
import { validateItemDraft, type ItemDraft } from "../lib/item-draft";
import { assertImportSellContract, catalogPriceError, MAX_CATALOG_PRICE_USD } from "../lib/sell-contract";
import type { Product } from "../lib/types";

/**
 * Cross-app catalog USD contract, shop side.
 *
 * The sell shop writes catalog.v1 and the intake app's shop-tools desk lists and
 * re-saves the very same Blob. scripts/testdata/catalog-usd-vectors.json records
 * which stored dollars that desk accepts; sassy-closet/tests/catalog-usd-contract
 * pins the desk itself. This file pins that no shop write, add, rename, import,
 * or live-catalog write can store a dollar the desk would refuse — that would
 * wedge every intake save until the Blob is edited by hand.
 *
 * Fixture dollars only. No catalog price, formula, or seed row is changed.
 */

const ROOT = path.join(process.cwd(), "..");
type Vector = { priceUsd: number; deskLists: boolean; case: string };
const VECTOR: Vector[] = JSON.parse(
  readFileSync(path.join(ROOT, "scripts", "testdata", "catalog-usd-vectors.json"), "utf8"),
).rows;
const MAX = JSON.parse(
  readFileSync(path.join(ROOT, "scripts", "testdata", "catalog-usd-vectors.json"), "utf8"),
).maxPriceUsd as number;

const SEED = JSON.parse(
  readFileSync(path.join(ROOT, "sassy-closet-shop", "data", "products.json"), "utf8"),
) as { products: Product[] };

const row = SEED.products[0] as Product;

function fields(priceUsd: number | null, status = "available") {
  return {
    ...messageReadyAddFields("A"),
    titleEn: row.titleEn,
    titleVn: row.titleVn,
    descriptionEn: row.descriptionEn,
    descriptionVn: row.descriptionVn,
    status,
    priceUsd,
    colors: row.colors,
    images: row.images,
    sizes: row.sizes,
    fitCm: row.fitCm,
    fulfillment: row.fulfillment,
    sourceLink: row.sourceLink,
  };
}

function draftWithPrice(priceInput: string, status: ItemDraft["status"] = "available"): ItemDraft {
  return {
    titleEn: row.titleEn,
    titleVn: row.titleVn,
    descriptionEn: row.descriptionEn,
    descriptionVn: row.descriptionVn,
    status,
    priceInput,
    colors: row.colors,
    images: row.images,
    sizes: row.sizes,
    fitCm: emptyFitCm(),
    fulfillment: row.fulfillment,
    sourceLink: "",
  };
}

test("vector loaded with both accepted and refused dollars", () => {
  assert.ok(VECTOR.length >= 12);
  assert.equal(MAX, MAX_CATALOG_PRICE_USD);
  assert.equal(VECTOR.filter((v) => v.deskLists).length > 0, true);
  assert.equal(VECTOR.filter((v) => !v.deskLists).length > 0, true);
});

test("catalogPriceError agrees with the desk verdict for every vector row", () => {
  const wrong = VECTOR.filter((v) => (catalogPriceError("A01", v.priceUsd) === null) !== v.deskLists);
  assert.deepEqual(wrong.map((v) => v.case), []);
});

test("the shop save gate refuses exactly the dollars the intake desk refuses", () => {
  const leaked = VECTOR.filter((v) => {
    try {
      productFromFields("A01", fields(v.priceUsd));
      return !v.deskLists;
    } catch {
      return false;
    }
  });
  assert.deepEqual(leaked.map((v) => v.case), []);
  // and it still accepts every readable dollar, so the fix is not a blanket block
  const blocked = VECTOR.filter((v) => v.deskLists && !productFromFields("A01", fields(v.priceUsd)));
  assert.deepEqual(blocked.map((v) => v.case), []);
});

test("the field editor blocks an unreadable price text before the save round-trip", () => {
  for (const v of VECTOR) {
    const invalid = validateItemDraft(draftWithPrice(String(v.priceUsd))) !== null;
    assert.equal(invalid, !v.deskLists, v.case);
  }
  // Hold clears the price box, so a stale unreadable text value must not block a hold save.
  assert.equal(validateItemDraft(draftWithPrice("20.005", "hold")), null);
});

test("no live catalog write can persist an unreadable dollar", () => {
  const catalog = (priceUsd: number): Product[] =>
    SEED.products.map((product) =>
      product.ma === row.ma ? { ...product, status: "available", priceUsd } : { ...product },
    );
  for (const v of VECTOR) {
    const write = () => assertLiveCatalogIntegrity(catalog(v.priceUsd));
    if (v.deskLists) {
      assert.doesNotThrow(write, v.case);
    } else {
      assert.throws(write, /A01/, v.case);
    }
  }
});

test("save, add, and hold mutations cannot store an unreadable dollar", () => {
  for (const v of VECTOR.filter((entry) => !entry.deskLists)) {
    const saved = saveProductInCatalog([row], "A01", fields(v.priceUsd));
    assert.equal(saved.ok, false, `save ${v.case}`);
    const held = saveProductInCatalog([row], "A01", fields(v.priceUsd, "hold"));
    assert.equal(held.ok, false, `hold ${v.case}`);
  }
});

test("a catalog import cannot land an unreadable dollar", () => {
  const clean = SEED.products.map((product) => ({ ...product }));
  assert.doesNotThrow(() => assertImportSellContract(clean));
  for (const v of VECTOR.filter((entry) => !entry.deskLists)) {
    const broken = clean.slice();
    broken[0] = { ...clean[0]!, status: "available", priceUsd: v.priceUsd };
    assert.throws(() => assertImportSellContract(broken), /A01/, v.case);
  }
});
