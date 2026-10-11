import assert from "node:assert/strict";
import test from "node:test";
import { addProductToCatalog, saveProductInCatalog, type ProductFieldsInput } from "../lib/admin-ops";
import type { Product } from "../lib/types";

function stub(ma: string, priceUsd: number): Product {
  return { ma, priceUsd } as Product;
}

function fields(priceUsd: number | null): ProductFieldsInput {
  return {
    titleEn: "",
    titleVn: "",
    descriptionEn: "",
    descriptionVn: "",
    status: "available",
    priceUsd,
    colors: [],
    images: [],
  };
}

test("shop mint does not emit Q02 or K06", () => {
  const queens = [stub("Q01", 20)];
  const mintedQueen = addProductToCatalog(queens, "Q", fields(20));
  assert.equal(mintedQueen.ok, false);
  if (!mintedQueen.ok) assert.match(mintedQueen.error, /Q02/);
  assert.deepEqual(
    queens.map((product) => product.ma),
    ["Q01"],
  );

  const knits = ["K01", "K02", "K03", "K04", "K05"].map((ma) => stub(ma, 36));
  const mintedKnit = addProductToCatalog(knits, "K", fields(36));
  assert.equal(mintedKnit.ok, false);
  if (!mintedKnit.ok) assert.match(mintedKnit.error, /K06/);
  assert.deepEqual(
    knits.map((product) => product.ma),
    ["K01", "K02", "K03", "K04", "K05"],
  );
});

test("shop save refuses an S06 dollar other than 25", () => {
  for (const priceUsd of [0, 24, 26, 40, 99]) {
    const catalog = [stub("S06", 25)];
    const saved = saveProductInCatalog(catalog, "S06", fields(priceUsd));
    assert.equal(saved.ok, false, String(priceUsd));
    if (!saved.ok) assert.match(saved.error, /\$25/);
    assert.equal(catalog[0]?.priceUsd, 25);
    assert.equal(catalog.length, 1);
  }

  const catalog = [stub("S06", 25)];
  const kept = saveProductInCatalog(catalog, "S06", fields(25));
  assert.equal(kept.ok, false);
  if (!kept.ok) assert.equal(kept.error.includes("$25"), false);
  assert.equal(catalog[0]?.priceUsd, 25);
});
