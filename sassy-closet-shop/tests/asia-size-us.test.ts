import assert from "node:assert/strict";
import test from "node:test";
import { parseAsiaSizes } from "../lib/asia-size";

test("a US size token is not read as an Asia letter", () => {
  assert.deepEqual(parseAsiaSizes(["S", "US M", "XXS", "2XL", "s"]), ["S", "2XS", "2XL"]);
  assert.deepEqual(parseAsiaSizes(["US M"]), []);
  assert.deepEqual(parseAsiaSizes(["M (US)"]), []);
  assert.deepEqual(parseAsiaSizes(["M US"]), []);
  assert.deepEqual(parseAsiaSizes(["美码 M"]), []);
  assert.deepEqual(parseAsiaSizes(["M美码"]), []);
  assert.deepEqual(parseAsiaSizes(["美国码 M"]), []);
  assert.deepEqual(parseAsiaSizes(["M美国码"]), []);
  assert.deepEqual(parseAsiaSizes(["M（US）"]), []);
});

test("a US note on another value keeps the Asia letter", () => {
  assert.deepEqual(parseAsiaSizes(["S (US 2-4)"]), ["S"]);
  assert.deepEqual(parseAsiaSizes(["M(US 6)"]), ["M"]);
  assert.deepEqual(parseAsiaSizes(["S 建议80-90斤 (US 2)"]), ["S"]);
  assert.deepEqual(parseAsiaSizes(["L / US 8"]), ["L"]);
  assert.deepEqual(parseAsiaSizes(["XL(建议120斤, US 10)"]), ["XL"]);
  assert.deepEqual(parseAsiaSizes(["M（US 6）"]), ["M"]);
});

test("a Taobao Asia label is still read", () => {
  assert.deepEqual(parseAsiaSizes(["S 建议80-90斤", "M女", "36"]), ["S", "M", "36"]);
});
