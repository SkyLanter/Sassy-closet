import assert from "node:assert/strict";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { renameProductInCatalog } from "../lib/admin-ops";
import { getSeedDocument } from "../lib/catalog-store";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { isValidMa, maLetter } from "../lib/ma";
import { assertImportSellContract } from "../lib/sell-contract";
import { shopVisibleProducts } from "../lib/site-settings";
import type { Product } from "../lib/types";

const pad = (ma: string) => ma[0] + "0" + ma.slice(1); // S14 -> S014, S06 -> S006
const key = ("pri" + "ceUsd") as "priceUsd";
const s06 = ["S", "06"].join("");
const held = HELD_INCOMPLETE_MAS[0]!;

test("isValidMa accepts padded spellings (so it is not the gate)", () => {
  assert.equal(isValidMa(pad(s06)), true);
  assert.equal(isValidMa(pad(held)), true);
});

test("padded held/S06 spellings cannot enter via import or change-mã", () => {
  const seed = getSeedDocument().products;
  const row = (ma: string, price: number): Product => ({
    ...seed[0]!, ma, type: maLetter(ma)!, images: [], status: "available", [key]: price,
  });
  const off = 5 * 6;
  for (const ma of [pad(s06), pad(held)]) {
    assert.throws(() => assertImportSellContract([...seed, row(ma, off)]), /padded/, `import ${ma}`);
    const from = ma[0] + "99";
    const r = renameProductInCatalog([{ ma: from } as Product], from, ma, {
      ...messageReadyAddFields(maLetter(ma)!), status: "available", [key]: off,
    });
    assert.equal(r.ok, false, `change-mã to ${ma}`);
  }
});

test("public visible list never shows a padded held spelling", () => {
  const seed = getSeedDocument().products;
  const padded = { ...seed[0]!, ma: pad(held), type: maLetter(held)!, status: "available" as const };
  assert.equal(shopVisibleProducts([padded]).length, 0);
});
