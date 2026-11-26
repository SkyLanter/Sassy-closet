import assert from "node:assert/strict";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { canonicalMaSpelling } from "../lib/ma";
import { productJsonLd, productSeo } from "../lib/seo";
import { toShopLook } from "../lib/shop-look";
import type { Product } from "../lib/types";

function row(ma: string, priceUsd: number | null): Product {
  return {
    ma,
    type: "A",
    titleVn: "Áo",
    titleEn: "Heather knit",
    priceUsd,
    qty: 1,
    status: priceUsd === null ? "hold" : "available",
    colors: [],
    images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "Heather knit",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

function withShopUrl<T>(run: () => T): T {
  const previous = process.env.NEXT_PUBLIC_SHOP_URL;
  process.env.NEXT_PUBLIC_SHOP_URL = "https://shop.example";
  try {
    return run();
  } finally {
    if (previous === undefined) {
      delete process.env.NEXT_PUBLIC_SHOP_URL;
    } else {
      process.env.NEXT_PUBLIC_SHOP_URL = previous;
    }
  }
}

test("customer look, canonical, and JSON-LD use the same mã spelling and keep the price", () => {
  for (const spelled of ["A1", "A001", "a01"]) {
    const price = 23;
    const look = toShopLook(row(spelled, price));
    assert.equal(look.ma, "A01", spelled);
    assert.equal(look.priceUsd, price, spelled);
    assert.equal(look.ma, canonicalMaSpelling(spelled));
    const seo = withShopUrl(() => productSeo(look));
    const canonical = seo.alternates && "canonical" in seo.alternates ? seo.alternates.canonical : "";
    assert.equal(canonical, "https://shop.example/m/A01", spelled);
    const jsonLd = withShopUrl(() => productJsonLd(look));
    assert.equal(jsonLd.sku, "A01", spelled);
    assert.equal(jsonLd.url, "https://shop.example/m/A01", spelled);
    const offer = jsonLd.offers as { price?: string };
    assert.equal(offer.price, "23.00", spelled);
  }

  const locked = toShopLook(row("S6", 25));
  assert.equal(locked.ma, "S06");
  assert.equal(locked.priceUsd, 25);
  const s06 = withShopUrl(() => productJsonLd(locked));
  assert.equal(s06.sku, "S06");
  assert.equal(s06.url, "https://shop.example/m/S06");
  assert.equal((s06.offers as { price?: string }).price, "25.00");

  const already = toShopLook(row("A15", 28));
  assert.equal(already.ma, "A15");
  assert.equal(already.priceUsd, 28);

  const stale = { ...already, ma: "A001", priceUsd: 28 };
  const fromStale = withShopUrl(() => productJsonLd(stale));
  assert.equal(fromStale.sku, "A01");
  assert.equal(fromStale.url, "https://shop.example/m/A01");
  assert.equal((fromStale.offers as { price?: string }).price, "28.00");
  const staleSeo = withShopUrl(() => productSeo(stale));
  const staleCanonical =
    staleSeo.alternates && "canonical" in staleSeo.alternates ? staleSeo.alternates.canonical : "";
  assert.equal(staleCanonical, "https://shop.example/m/A01");
});
