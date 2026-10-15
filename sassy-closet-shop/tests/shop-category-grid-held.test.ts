import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import held from "../../data/held.json";
import { categoryGridLooks } from "../lib/category-grid";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { maLetter, type MaLetter } from "../lib/ma";
import { parseCatalog } from "../lib/product-parse";
import { shopVisibleLooks } from "../lib/site-settings";
import fixtureRows from "./fixtures/shop-category-grid-held.json";

const HELD_FILE = new URL("../../data/held.json", import.meta.url);
const HELD_BYTES = readFileSync(HELD_FILE);

const products = parseCatalog(fixtureRows);
const heldSet = new Set(HELD_INCOMPLETE_MAS.map((ma) => ma.toUpperCase()));

const GRID_TYPES: MaLetter[] = ["S", "A", "K", "V"];

function gridMas(type: MaLetter): string[] {
  return categoryGridLooks(products, type).map((look) => look.ma);
}

test("shop category grid omits held mãs from the fixture and keeps S06 at $25", () => {
  assert.deepEqual([...HELD_INCOMPLETE_MAS], [...held.heldIncomplete]);
  assert.deepEqual(JSON.parse(HELD_BYTES.toString()).heldIncomplete, [...held.heldIncomplete]);
  assert.equal(heldSet.has("S06"), false);
  assert.equal(heldSet.has("A15"), false);

  const s06 = products.find((product) => product.ma === "S06");
  assert.equal(s06?.priceUsd, 25);
  const visible = shopVisibleLooks(products);
  assert.equal(visible.find((look) => look.ma === "S06")?.priceUsd, 25);
  assert.equal(visible.some((look) => heldSet.has(look.ma)), false);

  for (const ma of HELD_INCOMPLETE_MAS) {
    assert.equal(products.some((product) => product.ma === ma), true, ma);
  }

  assert.deepEqual(
    GRID_TYPES.flatMap((type) => gridMas(type)),
    ["S06", "A15"],
  );
  assert.deepEqual(gridMas("S"), ["S06"]);
  assert.deepEqual(gridMas("A"), ["A15"]);
  assert.deepEqual(gridMas("K"), []);
  assert.deepEqual(gridMas("V"), []);
  assert.equal(categoryGridLooks(products, "S").find((look) => look.ma === "S06")?.priceUsd, 25);

  for (const ma of HELD_INCOMPLETE_MAS) {
    const type = maLetter(ma);
    if (type === null) {
      throw new Error(`Held mã ${ma} has no category letter`);
    }
    assert.equal(gridMas(type).includes(ma), false, ma);
  }

  assert.equal(readFileSync(HELD_FILE).equals(HELD_BYTES), true);
  assert.equal(products.find((product) => product.ma === "S06")?.priceUsd, 25);
});
