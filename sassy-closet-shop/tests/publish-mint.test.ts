import assert from "node:assert/strict";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { addProductToCatalog, saveProductInCatalog, type ProductFieldsInput } from "../lib/admin-ops";
import { nextMaForLetter } from "../lib/ma";
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

test("shop letter Q mints Q02 on hold and still refuses K06", () => {
  assert.equal(nextMaForLetter("Q", ["Q01"]), "Q02");
  assert.equal(nextMaForLetter("Q", ["Q01", "Q02"]), "Q03");
  assert.equal(nextMaForLetter("P", ["P01"], ["P02", "P03"]), "P04");

  const queens = [stub("Q01", 20)];
  const mintedQueen = addProductToCatalog(queens, "Q", messageReadyAddFields("Q"));
  assert.equal(mintedQueen.ok, true);
  if (mintedQueen.ok) {
    assert.equal(mintedQueen.ma, "Q02");
    const queen = mintedQueen.products.find((product) => product.ma === "Q02");
    assert.equal(queen?.status, "hold");
    assert.equal(queen?.priceUsd, null);
  }
  assert.deepEqual(
    queens.map((product) => product.ma),
    ["Q01"],
  );

  const knits = ["K01", "K02", "K03", "K04", "K05"].map((ma) => stub(ma, 36));
  const mintedKnit = addProductToCatalog(knits, "K", fields(36));
  assert.equal(mintedKnit.ok, false);
  if (!mintedKnit.ok) assert.match(mintedKnit.error, /K06/);

  assert.equal(nextMaForLetter("G", []), "G01");
  const firstShoe = addProductToCatalog([], "G", messageReadyAddFields("G"));
  assert.equal(firstShoe.ok, false);
  if (!firstShoe.ok) assert.match(firstShoe.error, /G01/);
  assert.equal(nextMaForLetter("G", ["G01"]), "G02");
  const secondShoe = addProductToCatalog([stub("G01", 40)], "G", messageReadyAddFields("G"));
  assert.equal(secondShoe.ok, true);
  if (secondShoe.ok) assert.equal(secondShoe.ma, "G02");

  const nextHair = addProductToCatalog([stub("H01", 8)], "H", messageReadyAddFields("H"));
  assert.equal(nextHair.ok, false);
  if (!nextHair.ok) assert.match(nextHair.error, /H02/);
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
