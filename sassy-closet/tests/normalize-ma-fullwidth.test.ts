import assert from "node:assert/strict";
import test from "node:test";
import { normalizeMa } from "../lib/mint";

test("normalizeMa trims a BOM and does not fold fullwidth mã letters or digits", () => {
  assert.equal(normalizeMa("\uFEFFs6"), "S06");

  // Fullwidth stays fullwidth. Folding these to ASCII would fail this lock.
  assert.equal(normalizeMa("Ｓ０６"), "Ｓ０６");
  assert.notEqual(normalizeMa("Ｓ０６"), "S06");
  assert.equal(normalizeMa("A２４"), "A２４");
  assert.notEqual(normalizeMa("A２４"), "A24");
});
