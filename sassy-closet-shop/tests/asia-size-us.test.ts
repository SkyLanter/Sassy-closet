import assert from "node:assert/strict";
import test from "node:test";
import { parseAsiaSizes } from "../lib/asia-size";

test("a US size token is not read as an Asia letter", () => {
  assert.deepEqual(parseAsiaSizes(["S", "US M", "XXS", "2XL", "s"]), ["S", "2XS", "2XL"]);
  assert.deepEqual(parseAsiaSizes(["US M"]), []);
  assert.deepEqual(parseAsiaSizes(["M (US)"]), []);
});

test("a Taobao Asia label is still read", () => {
  assert.deepEqual(parseAsiaSizes(["S 建议80-90斤", "M女", "36"]), ["S", "M", "36"]);
});
