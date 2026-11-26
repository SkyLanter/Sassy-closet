import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { categoryJsonLd, jsonLdScriptHtml, organizationJsonLd, productJsonLd } from "../lib/seo";
import { toShopLook } from "../lib/shop-look";
import type { Product } from "../lib/types";

function row(): Product {
  return {
    ma: "A15",
    type: "A",
    titleVn: "Áo",
    titleEn: "Knit </script><p class=\"x\">",
    priceUsd: 23,
    qty: 1,
    status: "available",
    colors: [],
    images: [],
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "Soft </SCRIPT>",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

test("JSON-LD script HTML cannot close the tag and keeps the price", () => {
  const previous = process.env.NEXT_PUBLIC_SHOP_URL;
  process.env.NEXT_PUBLIC_SHOP_URL = "https://shop.example";
  try {
    const look = toShopLook(row());
    const data = productJsonLd(look);
    const html = jsonLdScriptHtml(data);
    assert.equal(html.toLowerCase().includes("</script"), false);
    assert.equal(html.includes("<"), false);
    assert.deepEqual(JSON.parse(html), JSON.parse(JSON.stringify(data)));
    assert.equal((data.offers as { price?: string }).price, "23.00");
    assert.equal(look.priceUsd, 23);

    const category = jsonLdScriptHtml(categoryJsonLd("Tops </script>", "ao", [look]));
    assert.equal(category.toLowerCase().includes("</script"), false);
    const categoryData = categoryJsonLd("Tops </script>", "ao", [look]);
    assert.deepEqual(JSON.parse(category), JSON.parse(JSON.stringify(categoryData)));

    const org = jsonLdScriptHtml(organizationJsonLd("https://facebook.com/example?q=</script>"));
    assert.equal(org.toLowerCase().includes("</script"), false);
    const orgData = organizationJsonLd("https://facebook.com/example?q=</script>");
    assert.deepEqual(JSON.parse(org), JSON.parse(JSON.stringify(orgData)));
  } finally {
    if (previous === undefined) delete process.env.NEXT_PUBLIC_SHOP_URL;
    else process.env.NEXT_PUBLIC_SHOP_URL = previous;
  }
});

test("shop pages embed JSON-LD through the escaped helper", () => {
  for (const rel of [
    "app/(shop)/m/[ma]/page.tsx",
    "app/(shop)/c/[slug]/page.tsx",
    "app/(shop)/(browse)/page.tsx",
  ]) {
    const src = readFileSync(path.join(process.cwd(), rel), "utf8");
    assert.equal(src.includes("jsonLdScriptHtml"), true, rel);
    assert.equal(src.includes("JSON.stringify("), false, rel);
  }
});
