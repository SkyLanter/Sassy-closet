import assert from "node:assert/strict";
import test from "node:test";
import { toggleAsiaLetter } from "../lib/asia-size";

test("adding an Asia letter keeps the EU shoe size", () => {
  assert.deepEqual(toggleAsiaLetter(["36"], "M"), ["M", "36"]);
  assert.deepEqual(toggleAsiaLetter(["M", "36"], "L"), ["M", "L", "36"]);
  assert.deepEqual(toggleAsiaLetter(["40", "S"], "M"), ["S", "M", "40"]);
});

test("removing an Asia letter keeps the EU shoe size", () => {
  assert.deepEqual(toggleAsiaLetter(["M", "36"], "M"), ["36"]);
  assert.deepEqual(toggleAsiaLetter(["L", "38", "XL"], "L"), ["38", "XL"]);
});

test("an Asia letter still toggles when no shoe size is set", () => {
  assert.deepEqual(toggleAsiaLetter([], "S"), ["S"]);
  assert.deepEqual(toggleAsiaLetter(["S", "M"], "S"), ["M"]);
});
