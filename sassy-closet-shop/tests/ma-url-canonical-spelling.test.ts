import assert from "node:assert/strict";
import test from "node:test";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { canonicalMaPath } from "../lib/ma-url";

test("padded, short and lower mã paths redirect to the canonical spelling", () => {
  assert.equal(canonicalMaPath("/m/a001"), "/m/A01");
  assert.equal(canonicalMaPath("/m/A001"), "/m/A01");
  assert.equal(canonicalMaPath("/m/a01"), "/m/A01");
  assert.equal(canonicalMaPath("/m/a1"), "/m/A01");
  assert.equal(canonicalMaPath("/m/%20a01%20"), "/m/A01");
  assert.equal(canonicalMaPath("/share/m/A001"), "/share/m/A01");
  assert.equal(canonicalMaPath("/m/A001/opengraph-image"), "/m/A01/opengraph-image");
  assert.equal(canonicalMaPath("/products/a1/cover.jpg"), "/products/A01/cover.jpg");
  assert.equal(canonicalMaPath("/products/A001/photo-2.jpg"), "/products/A01/photo-2.jpg");
  assert.equal(canonicalMaPath("/products/%20a01%20/cover.jpg"), "/products/A01/cover.jpg");
});

test("canonical mã paths, non-mã paths and invalid mãs are unchanged", () => {
  assert.equal(canonicalMaPath("/m/A01"), null);
  assert.equal(canonicalMaPath("/m/K03"), null);
  assert.equal(canonicalMaPath("/m/A100"), null);
  assert.equal(canonicalMaPath("/m/K003"), "/m/K03");
  assert.equal(canonicalMaPath("/c/ao"), null);
  assert.equal(canonicalMaPath("/m/hello"), null);
  assert.equal(canonicalMaPath("/m/%E0%A4%A"), null);
  assert.equal(canonicalMaPath("/products/A01/cover.jpg"), null);
  assert.equal(canonicalMaPath("/products/A100/cover.jpg"), null);
  assert.equal(canonicalMaPath("/products/hello/cover.jpg"), null);
  const held = HELD_INCOMPLETE_MAS[0]!;
  assert.equal(canonicalMaPath(`/products/${held}/cover.jpg`), null);
  assert.equal(canonicalMaPath(`/products/${held.toLowerCase()}/cover.jpg`), null);
  assert.equal(canonicalMaPath(`/products/${held[0]}0${held.slice(1)}/cover.jpg`), null);
});
