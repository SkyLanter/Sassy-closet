import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { maLetter } from "../lib/ma";
import { findShopProduct } from "../lib/products";
import { shopVisibleLooks, shopVisibleProducts } from "../lib/site-settings";
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
  const unpricedSold = { ...product("A03", "sold"), priceUsd: null };
  const hold = product("A02", "hold");
  const live = product("S06", "available");
  const catalog = [sold, unpricedSold, hold, live];
  const visible = shopVisibleProducts(catalog);

  assert.deepEqual(
    visible.map((item) => item.ma),
    ["A02", "S06"],
  );
  assert.deepEqual(
    shopVisibleLooks(catalog).map((item) => item.ma),
    ["A02", "S06"],
  );
  assert.equal(findShopProduct(visible, "a01"), undefined);
  assert.equal(findShopProduct(visible, "A1"), undefined);
  assert.equal(findShopProduct(visible, "A3"), undefined);
  assert.equal(findShopProduct(visible, "a002")?.ma, "A02");
  assert.equal(findShopProduct(visible, "a002")?.status, "hold");
  assert.equal(findShopProduct(visible, "a002")?.priceUsd, null);
  assert.equal(findShopProduct(catalog, "a01")?.status, "sold");
  assert.equal(findShopProduct(catalog, "a03")?.status, "sold");
  assert.equal(findShopProduct(catalog, "a03")?.priceUsd, null);

  const sitemap = readFileSync(path.join(process.cwd(), "app/sitemap.ts"), "utf8");
  assert.match(sitemap, /const products = shopVisibleProducts\(document\.products\);/);
  assert.match(sitemap, /\.\.\.products\.map\(\(product\) =>/);
  assert.equal(sitemap.includes("document.products.map"), false);

  const settings = readFileSync(path.join(process.cwd(), "lib/site-settings.ts"), "utf8");
  assert.match(settings, /return shopVisibleProducts\(products\)\.map\(toShopLook\);/);

  const productsSrc = readFileSync(path.join(process.cwd(), "lib/products.ts"), "utf8");
  assert.match(productsSrc, /return sortByPopular\(shopVisibleLooks\(document\.products\)\);/);
  assert.match(productsSrc, /return findShopProduct\(await getProducts\(\), ma\);/);

  const page = readFileSync(path.join(process.cwd(), "app/(shop)/m/[ma]/page.tsx"), "utf8");
  assert.equal(page.match(/await getProduct\(ma\)/g)?.length, 2);
});
