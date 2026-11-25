import assert from "node:assert/strict";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { productJsonLd } from "../lib/seo";
import { toShopLook } from "../lib/shop-look";
import type { Product } from "../lib/types";

function product(status: Product["status"], priceUsd: number | null): Product {
  return {
    ma: "A15",
    type: "A",
    titleVn: "Áo",
    titleEn: "Top",
    priceUsd,
    qty: 1,
    status,
    colors: [],
    images: [{ src: "/products/A15/cover.jpg", colorId: null, order: 1 }],
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "Heather knit",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

test("a look with no USD does not emit an Offer", () => {
  const look = toShopLook(product("hold", 25));
  assert.equal(look.priceUsd, null);
  const jsonLd = productJsonLd(look);
  assert.equal(jsonLd.offers, undefined);
  const html = JSON.stringify(jsonLd);
  assert.equal(html.includes("Offer"), false);
  assert.equal(html.includes("priceCurrency"), false);
  assert.equal(html.includes("availability"), false);
});

test("a priced look keeps a USD offer and does not invent availability", () => {
  const jsonLd = productJsonLd(toShopLook(product("available", 23)));
  const offer = jsonLd.offers as { price?: string; priceCurrency?: string; availability?: string };
  assert.equal(offer.price, "23.00");
  assert.equal(offer.priceCurrency, "USD");
  assert.equal(offer.availability, undefined);
  assert.equal(JSON.stringify(jsonLd).includes("availability"), false);
});
