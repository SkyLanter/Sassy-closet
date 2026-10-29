import assert from "node:assert/strict";
import test from "node:test";
import { decodeShopSearchHeader, encodeShopSearchHeader } from "../lib/look-search";

// The proxy encodes ?q on every home request. An emoji straddling the 80-char cap
// must not split into a lone surrogate (encodeURIComponent throws URIError -> 500).
test("search header cap never splits an emoji at the 80-char boundary", () => {
  const emoji = String.fromCodePoint(0x1f457);
  const query = "a".repeat(79) + emoji + "b";
  let encoded = "";
  assert.doesNotThrow(() => {
    encoded = encodeShopSearchHeader(query);
  });
  assert.equal(decodeShopSearchHeader(encoded), "a".repeat(79));
  assert.equal(decodeShopSearchHeader(encodeShopSearchHeader("a".repeat(78) + emoji)), "a".repeat(78) + emoji);
});
