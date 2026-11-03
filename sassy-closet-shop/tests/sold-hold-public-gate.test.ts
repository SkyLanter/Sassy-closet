import assert from "node:assert/strict";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { maLetter } from "../lib/ma";
import { findShopProduct } from "../lib/products";
import { shopVisibleProducts } from "../lib/site-settings";
import type { Product, ProductStatus } from "../lib/types";

function product(ma: string, status: ProductStatus): Product {
  const type = maLetter(ma);
  if (type === null) {
    throw new Error(`Invalid mã ${ma}`);
  }
  return {
    ma,
    type,
    titleVn: ma,
    titleEn: ma,
    priceUsd: status === "hold" ? null : 25,
    qty: 1,
    status,
    colors: [],
    images: [],
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

test("a sold piece stays off the public list while a hold piece stays on it", () => {
  const sold = product("A01", "sold");
  const hold = product("A02", "hold");
  const live = product("S06", "available");
  const catalog = [sold, hold, live];
  const visible = shopVisibleProducts(catalog);

  assert.deepEqual(
    visible.map((item) => item.ma),
    ["A02", "S06"],
  );
  assert.equal(findShopProduct(visible, "a01"), undefined);
  assert.equal(findShopProduct(visible, "A1"), undefined);
  assert.equal(findShopProduct(visible, "a002")?.ma, "A02");
  assert.equal(findShopProduct(visible, "a002")?.status, "hold");
  assert.equal(findShopProduct(catalog, "a01")?.status, "sold");
});
