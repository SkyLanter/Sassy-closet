import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { applyShopCatalogPatch, listShopCatalog, type ShopCatalogRow } from "../lib/shop-catalog";

/**
 * Cross-app colour-name contract, intake side.
 *
 * The intake shop-tools desk edits the same catalog.v1 Blob the sell shop reads.
 * The shop stores a colour name only when it is a real word: colors.ts
 * isStoredColorWord rejects a hex and a "Color #" placeholder, and
 * parseProductColor then persists an empty name, so the customer page shows
 * "Color 1" instead of what the desk thought it saved. The desk must refuse
 * that name instead of claiming a save the shop throws away.
 *
 * Fixture colours only. No catalog, price, held.json, or seed row changes.
 */

const ROOT = path.join(process.cwd(), "..");
type Vector = { name: string; shopStores: boolean; case: string };
const VECTOR: Vector[] = JSON.parse(
  readFileSync(path.join(ROOT, "scripts", "testdata", "color-name-vectors.json"), "utf8"),
).rows;

const ROW: Record<string, unknown> = {
  ma: "A01",
  titleVn: "Áo len puppy",
  titleEn: "Puppy cardigan",
  descriptionVn: "",
  descriptionEn: "",
  status: "available",
  priceUsd: 27,
  colors: [
    { id: "ca0100", hex: "#F5D76E", name: "Yellow", note: "" },
    { id: "ca0101", hex: "#7B5EA7", name: "Purple", note: "" },
  ],
};

function document(): Record<string, unknown> {
  return {
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    products: [{ ...ROW }],
  };
}

function saveColorName(name: string) {
  const doc = document();
  const listed = listShopCatalog(doc);
  assert.equal(listed.ok, true);
  const row = (listed as { products: ShopCatalogRow[] }).products[0]!;
  return applyShopCatalogPatch(
    doc,
    {
      ma: "A01",
      colors: row.colors.map((color, index) => (index === 0 ? { id: color.id, name } : { id: color.id, name: color.name })),
    },
    "2026-11-27T00:00:00.000Z",
  );
}

test("vector loaded with both storable and lossy colour names", () => {
  assert.ok(VECTOR.length >= 10);
  assert.equal(VECTOR.filter((row) => row.shopStores).length > 0, true);
  assert.equal(VECTOR.filter((row) => !row.shopStores).length > 0, true);
});

test("the desk refuses exactly the colour names the shop would throw away", () => {
  const wrong: string[] = [];
  for (const row of VECTOR) {
    const applied = saveColorName(row.name);
    if (applied.ok !== row.shopStores) {
      wrong.push(`${row.case} ${JSON.stringify(row.name)}: desk ${applied.ok ? "saved" : "refused"}`);
    }
  }
  assert.deepEqual(wrong, []);
});

test("a storable colour name is written back unchanged and trimmed", () => {
  const applied = saveColorName("  Kem  ");
  assert.equal(applied.ok, true);
  if (applied.ok) {
    const parsed = JSON.parse(applied.json) as { products: { colors: { name: string }[] }[] };
    assert.equal(parsed.products[0]?.colors[0]?.name, "Kem");
  }
});

test("a refused name leaves the stored catalog untouched", () => {
  const applied = saveColorName("#F4F0E8");
  assert.equal(applied.ok, false);
  if (!applied.ok) {
    assert.match(applied.error, /A01/);
    assert.match(applied.error, /color name/);
  }
});

test("every colour the seed stores is still storable, so the gate is not a blanket block", () => {
  const seed = JSON.parse(
    readFileSync(path.join(ROOT, "sassy-closet-shop", "data", "products.json"), "utf8"),
  ) as { products: { ma: string; colors: { name: string }[] }[] };
  for (const product of seed.products) {
    for (const color of product.colors) {
      // Hub colours use Vietnamese words; the seed must never need a hex as a name.
      const applied = saveColorName(color.name);
      assert.equal(applied.ok, true, `${product.ma} ${JSON.stringify(color.name)}`);
    }
  }
});
