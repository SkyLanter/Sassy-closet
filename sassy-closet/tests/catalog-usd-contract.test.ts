import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { listShopCatalog, type ShopCatalogRow } from "../lib/shop-catalog";

/**
 * Cross-app catalog USD contract, intake side.
 *
 * The sell shop writes catalog.v1 and this intake desk lists and re-saves that
 * same Blob. scripts/testdata/catalog-usd-vectors.json is the one list of stored
 * dollars both apps agree on; sassy-closet-shop/tests/catalog-usd-contract.test
 * pins that no shop write can create a dollar this desk refuses.
 *
 * Fixture dollars only. No catalog price, formula, or seed row is changed.
 */

const ROOT = path.join(process.cwd(), "..");
const FILE = JSON.parse(
  readFileSync(path.join(ROOT, "scripts", "testdata", "catalog-usd-vectors.json"), "utf8"),
) as { maxPriceUsd: number; rows: { priceUsd: number; deskLists: boolean; case: string }[] };

const ROW: Record<string, unknown> = {
  ma: "A01",
  titleVn: "Áo len puppy",
  titleEn: "Puppy cardigan",
  descriptionVn: "",
  descriptionEn: "",
  status: "available",
  colors: [],
};

function document(priceUsd: number): Record<string, unknown> {
  return {
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    products: [{ ...ROW, priceUsd }],
  };
}

test("vector loaded with both accepted and refused dollars", () => {
  assert.ok(FILE.rows.length >= 12);
  assert.equal(FILE.rows.filter((row) => row.deskLists).length > 0, true);
  assert.equal(FILE.rows.filter((row) => !row.deskLists).length > 0, true);
});

test("the desk lists a stored dollar exactly when the shared vector says it can", () => {
  const wrong: string[] = [];
  for (const row of FILE.rows) {
    const listed = listShopCatalog(document(row.priceUsd));
    if (listed.ok !== row.deskLists) {
      wrong.push(`${row.case} ($${row.priceUsd}): desk ${listed.ok ? "listed" : "refused"}`);
    }
  }
  assert.deepEqual(wrong, []);
});

test("a refused dollar is refused for the whole file, so one row wedges every save", () => {
  const listed = listShopCatalog(document(20.005));
  assert.equal(listed.ok, false);
  if (!listed.ok) {
    assert.match(listed.error, /dollars and cents/);
  }
  const huge = listShopCatalog(document(100001));
  assert.equal(huge.ok, false);
  if (!huge.ok) {
    assert.match(huge.error, /invalid USD price/);
  }
});

test("the desk keeps every readable dollar unchanged", () => {
  for (const value of [0, 1, 27, 27.5, 27.99, FILE.maxPriceUsd]) {
    const listed = listShopCatalog(document(value));
    assert.equal(listed.ok, true, String(value));
    if (listed.ok) {
      const rows = listed.products as ShopCatalogRow[];
      assert.equal(rows[0]?.priceUsd, value, String(value));
    }
  }
});
