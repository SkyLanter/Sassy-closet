import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { canonicalMaSpelling, isCanonicalMaSpelling } from "../lib/ma";

// Shared with scripts/held_policy.py norm_ma and sassy-closet/lib/mint normalizeMa.
type Row = { input: string | null; expected: string; case: string };
const VECTOR: Row[] = JSON.parse(
  readFileSync(path.join(process.cwd(), "..", "scripts", "testdata", "ma-normalization-vectors.json"), "utf8"),
).rows;

test("vector loaded", () => assert.ok(VECTOR.length >= 40));

test("canonicalMaSpelling matches the shared vector", () => {
  for (const row of VECTOR) {
    // Mapping: TS takes a string, so a null (None) row is checked as "" (Python None -> "").
    const input = row.input ?? "";
    assert.equal(canonicalMaSpelling(input), row.expected, `input ${JSON.stringify(row.input)}`);
    assert.equal(
      isCanonicalMaSpelling(input),
      row.expected === input.trim().toUpperCase(),
      `isCanonical ${JSON.stringify(row.input)}`,
    );
  }
});
