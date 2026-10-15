import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import held from "../../data/held.json";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import {
  exactMaLook,
  filterLooksByQuery,
  lookSearchHref,
  resolveLookSearch,
  suggestLooks,
  toLookSearchItems,
  type LookSearchItem,
} from "../lib/look-search";
import { parseCatalog } from "../lib/product-parse";
import { shopVisibleLooks } from "../lib/site-settings";
import fixtureRows from "./fixtures/shop-search-held.json";

const HELD_FILE = new URL("../../data/held.json", import.meta.url);
const HELD_BYTES = readFileSync(HELD_FILE);

const products = parseCatalog(fixtureRows);
const looks: LookSearchItem[] = toLookSearchItems(products);
const heldSet = new Set(HELD_INCOMPLETE_MAS.map((ma) => ma.toUpperCase()));

function queriesFor(ma: string): string[] {
  const letter = ma.slice(0, 1);
  const digits = ma.slice(1);
  return [ma, ma.toLowerCase(), `${letter} ${digits}`, `${letter.toLowerCase()}-${digits}`];
}

test("shop search omits held mãs from the fixture and keeps S06 at $25", () => {
  assert.deepEqual([...HELD_INCOMPLETE_MAS], [...held.heldIncomplete]);
  assert.deepEqual(JSON.parse(HELD_BYTES.toString()).heldIncomplete, [...held.heldIncomplete]);
  assert.equal(heldSet.has("S06"), false);
  assert.equal(heldSet.has("A15"), false);

  const s06 = products.find((product) => product.ma === "S06");
  assert.equal(s06?.priceUsd, 25);
  const visible = shopVisibleLooks(products);
  assert.equal(visible.find((look) => look.ma === "S06")?.priceUsd, 25);
  assert.equal(visible.some((look) => heldSet.has(look.ma)), false);

  assert.deepEqual(
    filterLooksByQuery(looks, "").map((look) => look.ma),
    ["S06", "A15"],
  );
  assert.deepEqual(filterLooksByQuery(looks, "held piece").map((look) => look.ma), []);
  assert.deepEqual(suggestLooks(looks, "held piece").map((look) => look.ma), []);
  assert.deepEqual(filterLooksByQuery(looks, "S06").map((look) => look.ma), ["S06"]);
  assert.equal(exactMaLook(looks, "s 06")?.ma, "S06");
  assert.equal(lookSearchHref(resolveLookSearch(looks, "S06")), "/m/S06");
  assert.deepEqual(filterLooksByQuery(looks, "heather").map((look) => look.ma), ["A15"]);
  assert.deepEqual(filterLooksByQuery(visible, "S06").map((look) => look.ma), ["S06"]);

  for (const ma of HELD_INCOMPLETE_MAS) {
    assert.equal(looks.some((look) => look.ma === ma), true, ma);
    for (const query of queriesFor(ma)) {
      const grid = filterLooksByQuery(looks, query).map((look) => look.ma);
      const suggestions = suggestLooks(looks, query).map((look) => look.ma);
      assert.equal(grid.includes(ma), false, query);
      assert.equal(suggestions.includes(ma), false, query);
      assert.equal(exactMaLook(looks, query)?.ma, undefined, query);
      const resolution = resolveLookSearch(looks, query);
      assert.equal(resolution.kind, "results", query);
      assert.equal(lookSearchHref(resolution).includes(`/m/${ma}`), false, query);
    }
  }

  assert.equal(readFileSync(HELD_FILE).equals(HELD_BYTES), true);
  assert.equal(products.find((product) => product.ma === "S06")?.priceUsd, 25);
});
