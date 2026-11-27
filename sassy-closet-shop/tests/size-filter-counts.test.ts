import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { countLooksByType } from "../lib/shop-sizes";

const LOOKS = [
  { type: "A", sizes: ["S", "M"] },
  { type: "A", sizes: ["L"] },
  { type: "S", sizes: ["M"] },
  { type: "D", sizes: [] },
];

test("a size chip counts only looks that carry that letter", () => {
  assert.deepEqual(countLooksByType(LOOKS, ["A", "S", "D"], null), {
    all: 4,
    A: 2,
    S: 1,
    D: 1,
  });
  assert.deepEqual(countLooksByType(LOOKS, ["A", "S", "D"], "M"), {
    all: 2,
    A: 1,
    S: 1,
    D: 0,
  });
  assert.deepEqual(countLooksByType(LOOKS, ["A", "S", "D"], "L"), {
    all: 1,
    A: 1,
    S: 0,
    D: 0,
  });
});

test("home tabs pass the active size into the same count", () => {
  const source = readFileSync(new URL("../components/featured-board.tsx", import.meta.url), "utf8");
  const start = source.indexOf("const counts = useMemo");
  const end = source.indexOf("const browseCount", start);
  const block = source.slice(start, end);
  assert.match(block, /countLooksByType\(searched, types, activeSize\)/);
  assert.equal(block.includes("searched.length"), false);
});
