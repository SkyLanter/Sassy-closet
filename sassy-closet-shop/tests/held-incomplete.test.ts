import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import held from "../../data/held.json";
import { emptyFitCm } from "../lib/asia-size";
import { HELD_INCOMPLETE_MAS, NEVER_LIST_MAS, isHeldIncompleteMa, isOffLiveSell } from "../lib/held-incomplete";
import { maLetter } from "../lib/ma";
import { shopVisibleProducts } from "../lib/site-settings";
import type { Product } from "../lib/types";

function product(ma: string, priceUsd: number): Product {
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

test("sell site loads held mãs from data/held.json", () => {
  assert.deepEqual([...HELD_INCOMPLETE_MAS], [...held.heldIncomplete]);
  assert.deepEqual([...NEVER_LIST_MAS], [...held.neverList]);
  assert.equal(isHeldIncompleteMa("K06"), true);
  assert.equal(isHeldIncompleteMa("V05"), true);
  assert.equal(isHeldIncompleteMa("Q02"), false);
  assert.equal(isOffLiveSell("Q02"), false);
  assert.equal(isOffLiveSell("A07"), false);
  assert.equal(isOffLiveSell("S10"), false);
  const source = readFileSync(new URL("../lib/held-incomplete.ts", import.meta.url), "utf8");
  assert.match(source, /data\/held\.json/);
  assert.equal(source.includes('["S14"'), false);
});

test("public catalog hides held mãs and keeps Q02, A07, and S10", () => {
  const visible = shopVisibleProducts([
    product("S14", 20),
    product("K06", 48),
    product("V05", 27),
    product("Q02", 20),
    product("A07", 26),
    product("S10", 37),
    product("S06", 25),
  ]).map((item) => item.ma);
  assert.deepEqual(visible, ["Q02", "A07", "S10", "S06"]);
});
