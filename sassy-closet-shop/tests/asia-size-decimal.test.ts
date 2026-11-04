import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { catalogSizeLetters, parseAsiaSizes } from "../lib/asia-size";

test("parseAsiaSizes keeps an exact NN.0 EU chip and drops other decimals", () => {
  assert.deepEqual(parseAsiaSizes(["40.0"]), ["40"]);
  assert.deepEqual(parseAsiaSizes(["34.0", "42.0", "35.0"]), ["34", "42", "35"]);
  assert.deepEqual(parseAsiaSizes(["33.0"]), []);
  assert.deepEqual(parseAsiaSizes(["46.0"]), []);
  assert.deepEqual(parseAsiaSizes(["4.0"]), []);
  assert.deepEqual(parseAsiaSizes(["35.00"]), []);
  assert.deepEqual(parseAsiaSizes(["34.5"]), []);
  assert.deepEqual(parseAsiaSizes(["40.00"]), []);
  assert.deepEqual(parseAsiaSizes(["40"]), ["40"]);
  assert.deepEqual(parseAsiaSizes([40]), ["40"]);
  assert.deepEqual(parseAsiaSizes(["40码"]), ["40"]);
  assert.deepEqual(parseAsiaSizes(["EU40"]), ["40"]);
  assert.deepEqual(parseAsiaSizes(["40."]), ["40"]);
  assert.deepEqual(parseAsiaSizes(["36 -37"]), []);
  assert.deepEqual(parseAsiaSizes(["S", "40.0"]), ["S", "40"]);
  assert.deepEqual(parseAsiaSizes(["XXS", "XXL"]), ["2XS", "2XL"]);
  assert.deepEqual(parseAsiaSizes(["40.0", "40"]), ["40"]);
});

test("catalog letter row drops the EU chip parsed from NN.0", () => {
  assert.deepEqual(catalogSizeLetters(parseAsiaSizes(["40.0", "S"])), ["S"]);
});

test("catalogSizeLetters still filters with ASIA_SIZE_LETTERS only", () => {
  const source = readFileSync(new URL("../lib/asia-size.ts", import.meta.url), "utf8");
  const start = source.indexOf("export function catalogSizeLetters");
  assert.ok(start >= 0, "catalogSizeLetters is exported from lib/asia-size.ts");
  const open = source.indexOf("{", start);
  assert.ok(open > start);
  let depth = 0;
  let end = -1;
  for (let i = open; i < source.length; i += 1) {
    const char = source[i];
    if (char === "{") {
      depth += 1;
    } else if (char === "}") {
      depth -= 1;
      if (depth === 0) {
        end = i;
        break;
      }
    }
  }
  assert.ok(end > open, "catalogSizeLetters function body is closed");
  const body = source.slice(open, end + 1);
  assert.match(body, /return ASIA_SIZE_LETTERS\.filter\b/);
});
