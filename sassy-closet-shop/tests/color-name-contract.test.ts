import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { isStoredColorWord, parseProductColor, colorShopLabel } from "../lib/colors";

/**
 * Cross-app colour-name contract, shop side.
 *
 * The intake shop-tools desk writes a colour name into the same catalog.v1 Blob
 * this app reads. scripts/testdata/color-name-vectors.json is the one list of
 * names that survive; sassy-closet/tests/color-name-contract pins that the desk
 * refuses the rest instead of claiming a save. This file pins the shop rule that
 * decides it, so the two apps cannot drift.
 *
 * Fixture colours only. No catalog, price, or seed row is changed.
 */

const ROOT = path.join(process.cwd(), "..");
type Vector = { name: string; shopStores: boolean; case: string };
const ROWS: Vector[] = JSON.parse(
  readFileSync(path.join(ROOT, "scripts", "testdata", "color-name-vectors.json"), "utf8"),
).rows;

test("vector loaded with both storable and lossy names", () => {
  assert.ok(ROWS.length >= 10);
  assert.equal(ROWS.filter((row) => row.shopStores).length > 0, true);
  assert.equal(ROWS.filter((row) => !row.shopStores).length > 0, true);
});

test("isStoredColorWord agrees with the shared vector", () => {
  const wrong = ROWS.filter((row) => isStoredColorWord(row.name) !== row.shopStores);
  assert.deepEqual(wrong.map((row) => `${row.case} ${JSON.stringify(row.name)}`), []);
});

test("a name the desk must refuse is the name parseProductColor throws away", () => {
  for (const row of ROWS.filter((entry) => !entry.shopStores)) {
    const color = parseProductColor({ id: "ca0100", hex: "#F5D76E", name: row.name, note: "" }, "A01", 0);
    assert.equal(color.name, "", `${row.case}: the shop stores an empty name`);
    // The customer then sees a positional fallback, not the name the desk typed.
    assert.equal(colorShopLabel(color, 0), "Color 1", row.case);
  }
});

test("a name the desk may keep is the name the customer sees", () => {
  for (const row of ROWS.filter((entry) => entry.shopStores)) {
    const color = parseProductColor({ id: "ca0100", hex: "#F5D76E", name: row.name, note: "" }, "A01", 0);
    assert.equal(color.name, row.name.trim(), row.case);
    assert.equal(colorShopLabel(color, 0), row.name.trim(), row.case);
  }
});

test("every colour the seed stores already survives the rule", () => {
  const seed = JSON.parse(
    readFileSync(path.join(ROOT, "sassy-closet-shop", "data", "products.json"), "utf8"),
  ) as { products: { ma: string; colors: { id: string; hex: string; name: string; note: string }[] }[] };
  for (const product of seed.products) {
    for (const color of product.colors) {
      assert.equal(isStoredColorWord(color.name), true, `${product.ma} ${JSON.stringify(color.name)}`);
    }
  }
});
