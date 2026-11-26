import assert from "node:assert/strict";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { ownMaImages } from "../lib/product-media";
import { shopVisibleLooks, shopVisibleProducts } from "../lib/site-settings";
import type { Product } from "../lib/types";

function row(ma: string, images: Array<{ src: string }>): Product {
  return {
    ma,
    type: "A",
    titleVn: "Áo",
    titleEn: "Top",
    priceUsd: 25,
    qty: 1,
    status: "available",
    colors: [],
    images: images.map((image, index) => ({ src: image.src, colorId: null, order: index + 1 })),
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

/**
 * Shop README: "Looks with no own photos stay in admin, not the shop."
 * A photo-less row used to publish a "Sassy Closet / mã" placeholder tile in
 * the grid, a placeholder PDP, and a sitemap URL for that placeholder page.
 * The admin catalog still keeps the row so Boss can finish it.
 */
test("a look with no own photos is not listed on the shop", () => {
  const photoLess = row("A03", []);
  assert.equal(ownMaImages(photoLess).length, 0);
  assert.deepEqual(shopVisibleLooks([photoLess]), []);
  assert.deepEqual(
    shopVisibleProducts([photoLess]).map((product) => product.ma),
    ["A03"],
    "admin keeps the row",
  );
});

test("a look whose only photos belong to another mã is not listed", () => {
  const foreign = row("A04", [{ src: "/products/A01/cover.jpg" }]);
  assert.equal(shopVisibleLooks([foreign]).length, 0);
  assert.equal(shopVisibleProducts([foreign]).length, 1, "admin keeps the row");
});

test("a look with its own photo still lists, at the same price", () => {
  const priced = row("A05", [{ src: "/products/A05/cover.jpg" }]);
  priced.priceUsd = 27;
  assert.deepEqual(
    shopVisibleLooks([priced]).map((look) => [look.ma, look.priceUsd, look.images.length]),
    [["A05", 27, 1]],
  );
});
