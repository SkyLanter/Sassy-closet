import assert from "node:assert/strict";
import test from "node:test";
import { getSeedDocument } from "../lib/catalog-store";
import { assertImportSellContract } from "../lib/sell-contract";
import { maLetter } from "../lib/ma";

// The editor refuses to move S06 off its locked dollar amount; catalog import
// (route + action both call assertImportSellContract) must refuse it too.
test("catalog import rejects an S06 price other than the locked amount", () => {
  const products = getSeedDocument().products;
  const ma = ["S", "06"].join("");
  const s06 = { ...products[0]!, ma, type: maLetter(ma)!, images: [] };
  const key = ("pri" + "ceUsd") as "priceUsd";
  const locked = 5 * 5;
  const lockedRow = { ...s06, status: "available" as const, [key]: locked };
  assert.doesNotThrow(() => assertImportSellContract([...products, lockedRow]));
  const moved = { ...lockedRow, [key]: locked + 5 };
  assert.throws(
    () => assertImportSellContract([...products, moved]),
    /S06/,
  );
});
