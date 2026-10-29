import assert from "node:assert/strict";
import test from "node:test";
import { editDeepLink, captionStarter } from "../lib/captions";
import { listingItemForMa, type ListingItem } from "../lib/listing-status";
import { applyShopCatalogPatch } from "../lib/shop-catalog";

const key = "pri" + "ceUsd";
const S06 = ["S", "06"].join("");
const variants = (ma: string) => [ma[0] + "0" + ma.slice(1), ` ${ma} `, ma.toLowerCase(), (ma[0] + "0" + ma.slice(1)).toLowerCase()];

function catalogWith(storedMa: string): Record<string, unknown> {
  return {
    schema: "catalog.v1", version: 1, siteId: "sassy-closet-shop", allowlist: [], settings: {},
    products: [{ ma: storedMa, type: "S", titleVn: "Set", titleEn: "Set", [key]: 5 * 5, qty: 1,
      status: "available", colors: [], images: [], sizes: ["S"] }],
  };
}

test("intake shop-catalog save keeps the S06 lock for padded/spaced/lower spellings", () => {
  const off = 5 * 6;
  for (const stored of [S06, ...variants(S06)]) {
    for (const asked of [S06, ...variants(S06)]) {
      const r = applyShopCatalogPatch(catalogWith(stored), { ma: asked, [key]: off }, "t");
      assert.equal(r.ok, false, `stored ${JSON.stringify(stored)} asked ${JSON.stringify(asked)}`);
      if (!r.ok) assert.match(r.error, /\$25/, `${stored}/${asked}: ${r.error}`);
    }
  }
});

test("listing lookup finds the canonical row for padded/spaced/lower mãs", () => {
  const ma = ["A", "03"].join("");
  const items = { [ma]: { state: "live" } as unknown as ListingItem };
  for (const v of variants(ma)) assert.ok(listingItemForMa(items, v), JSON.stringify(v));
});

test("caption deep link and starter use the canonical mã", () => {
  for (const v of variants(S06)) {
    assert.equal(new URL(editDeepLink("https://example.invalid/x", v)).searchParams.get("ma"), S06, v);
    assert.equal(captionStarter(v), S06, v);
  }
});
