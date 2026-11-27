import assert from "node:assert/strict";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { coverSrc, srcBelongsToMa } from "../lib/product-media";
import { productJsonLd } from "../lib/seo";
import { toShopLook } from "../lib/shop-look";
import type { Product } from "../lib/types";

function row(ma: string, images: Product["images"]): Product {
  return {
    ma,
    type: "A",
    titleVn: "Áo",
    titleEn: "Cardigan",
    priceUsd: 23,
    qty: 1,
    status: "available",
    colors: [],
    images,
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "Soft cardigan",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

test("the same mã keeps its canonical photo folder", () => {
  assert.equal(srcBelongsToMa("/products/A02/cover.jpg", "A02"), true);
  assert.equal(srcBelongsToMa("/products/A02/cover.jpg", "A2"), true);
  assert.equal(srcBelongsToMa("/products/A02/cover.jpg", "A002"), true);
  assert.equal(srcBelongsToMa("/products/a02/cover.jpg", "A02"), true);
  assert.equal(srcBelongsToMa("/products/A01/cover.jpg", "A02"), false);
  assert.equal(srcBelongsToMa("/products/a01/cover.jpg", "A02"), false);
  assert.equal(srcBelongsToMa("/products/A001/cover.jpg", "A02"), false);
  assert.equal(srcBelongsToMa("/products/A04/cover.jpg", "A03"), true);
});

test("shop look, JSON-LD, and cover use the own folder and keep the price", () => {
  const look = toShopLook(
    row("A2", [
      { src: "/products/A02/cover.jpg", colorId: null, order: 1 },
      { src: "/products/a01/cover.jpg", colorId: null, order: 2 },
    ]),
  );
  assert.deepEqual(
    look.images.map((image) => image.src),
    ["/products/A02/cover.jpg"],
  );
  assert.equal(look.priceUsd, 23);
  assert.equal(coverSrc(look), "/products/A02/cover.jpg");
  const jsonLd = productJsonLd(look);
  const offer = jsonLd.offers as { price?: string };
  const images = Array.isArray(jsonLd.image) ? jsonLd.image.map(String) : [];
  assert.equal(offer.price, "23.00");
  assert.equal(images.length, 1);
  assert.equal(images[0]?.includes("/products/A02/cover.jpg"), true);
  assert.equal(images.some((src) => src.toLowerCase().includes("/products/a01/")), false);
});
