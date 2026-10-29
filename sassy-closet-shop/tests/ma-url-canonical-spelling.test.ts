import assert from "node:assert/strict";
import test from "node:test";
import { canonicalMaPath } from "../lib/ma-url";

test("padded, short and lower mã paths redirect to the canonical spelling", () => {
  assert.equal(canonicalMaPath("/m/a001"), "/m/A01");
  assert.equal(canonicalMaPath("/m/A001"), "/m/A01");
  assert.equal(canonicalMaPath("/m/a01"), "/m/A01");
  assert.equal(canonicalMaPath("/m/a1"), "/m/A01");
  assert.equal(canonicalMaPath("/m/%20a01%20"), "/m/A01");
  assert.equal(canonicalMaPath("/share/m/A001"), "/share/m/A01");
  assert.equal(canonicalMaPath("/m/A001/opengraph-image"), "/m/A01/opengraph-image");
});

test("canonical mã paths, non-mã paths and invalid mãs are unchanged", () => {
  assert.equal(canonicalMaPath("/m/A01"), null);
  assert.equal(canonicalMaPath("/m/K03"), null);
  assert.equal(canonicalMaPath("/m/A100"), null);
  assert.equal(canonicalMaPath("/m/K003"), "/m/K03");
  assert.equal(canonicalMaPath("/c/ao"), null);
  assert.equal(canonicalMaPath("/m/hello"), null);
  assert.equal(canonicalMaPath("/m/%E0%A4%A"), null);
});
