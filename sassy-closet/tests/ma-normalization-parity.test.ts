import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { canonicalHeldKey } from "../lib/held-incomplete";
import { normalizeMa } from "../lib/mint";

// Shared with scripts/held_policy.py norm_ma and sassy-closet-shop/lib/ma canonicalMaSpelling.
type Row = { input: string | null; expected: string; case: string };
const VECTOR: Row[] = JSON.parse(
  readFileSync(path.join(process.cwd(), "..", "scripts", "testdata", "ma-normalization-vectors.json"), "utf8"),
).rows;

test("vector loaded", () => assert.ok(VECTOR.length >= 40));

test("mint normalizeMa matches the shared vector", () => {
  for (const row of VECTOR) {
    // Mapping: null (None) row is checked as "". No other mapping: mint agrees on every row.
    const input = row.input ?? "";
    assert.equal(normalizeMa(input), row.expected, `input ${JSON.stringify(row.input)}`);
  }
});

test("held-incomplete canonicalHeldKey matches the shared vector", () => {
  for (const row of VECTOR) {
    assert.equal(canonicalHeldKey(row.input ?? ""), row.expected, `input ${JSON.stringify(row.input)}`);
  }
});
