import assert from "node:assert/strict";
import test from "node:test";
import { fbRankOf, sortShopLooks } from "../lib/fb-rank";
import { popularScore, sortByPopular } from "../lib/popular-rank";

const META_HEAD = ["A05", "S05", "A01", "O05", "A06", "O04", "S03", "S07"];

test("Looks Popular follows Meta popular-order, not the 90-day FB views table", () => {
  const shuffled = ["A01", "A11", "S03", "S02", "A05", "S05", "A06", "S07", "O04", "A15", "O05", "Z99"].map(
    (ma) => ({ ma }),
  );
  const popular = sortShopLooks(shuffled, "popular").map((item) => item.ma);
  assert.deepEqual(popular.slice(0, META_HEAD.length), META_HEAD);
  assert.equal(popular.at(-1), "Z99");
  assert.notDeepEqual(popular.slice(0, 4), ["A01", "A11", "S03", "S02"]);
  assert.deepEqual(
    sortByPopular(shuffled).map((item) => item.ma),
    popular,
  );
});

test("a padded or short spelling keeps that mã's Meta rank", () => {
  const ranked = sortByPopular([
    { ma: "S05" },
    { ma: "A005" },
    { ma: "a5" },
    { ma: "Z99" },
  ]).map((item) => item.ma);
  assert.deepEqual(ranked, ["A005", "a5", "S05", "Z99"]);
  assert.equal(popularScore("A005"), popularScore("A05"));
  assert.ok(popularScore("A05") > 0);
  assert.equal(fbRankOf("A001"), fbRankOf("A01"));
  assert.equal(fbRankOf("a1"), 1);
});

test("Mã sort stays letter order and does not apply Popular", () => {
  const items = ["S03", "A11", "A01", "A05"].map((ma) => ({ ma }));
  assert.deepEqual(
    sortShopLooks(items, "ma").map((item) => item.ma),
    ["A01", "A05", "A11", "S03"],
  );
});
