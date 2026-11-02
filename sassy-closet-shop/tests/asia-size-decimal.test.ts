import assert from "node:assert/strict";
import test from "node:test";
import { parseAsiaSizes } from "../lib/asia-size";

test("trailing .0 is the two-digit EU size", () => {
  assert.deepEqual(parseAsiaSizes(["34.0"]), ["34"]);
  assert.deepEqual(parseAsiaSizes(["40.0"]), ["40"]);
  assert.deepEqual(parseAsiaSizes([" 42.0 "]), ["42"]);
  assert.deepEqual(parseAsiaSizes([40]), ["40"]);
  assert.deepEqual(parseAsiaSizes(["40.0", "40", "34.0"]), ["40", "34"]);
});

test("a longer fraction or a size range is not an EU size", () => {
  assert.deepEqual(parseAsiaSizes(["34.00"]), []);
  assert.deepEqual(parseAsiaSizes(["34.5"]), []);
  assert.deepEqual(parseAsiaSizes(["40.00"]), []);
  assert.deepEqual(parseAsiaSizes(["33.0"]), []);
  assert.deepEqual(parseAsiaSizes(["46.0"]), []);
  assert.deepEqual(parseAsiaSizes(["36 -37(适合平时35-36码)"]), []);
  assert.deepEqual(parseAsiaSizes(["S 建议80-90斤"]), ["S"]);
  assert.deepEqual(parseAsiaSizes(["S", "US M", "XXS", "2XL", "s"]), ["S", "M", "2XS", "2XL"]);
});
