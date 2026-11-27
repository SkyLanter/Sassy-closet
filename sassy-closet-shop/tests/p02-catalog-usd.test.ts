import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { overlayCustomerStockVoice } from "../lib/catalog-store";
import { parseCatalogDocument } from "../lib/product-parse";
import { productJsonLd } from "../lib/seo";

test("P02 and P05 stay available at the catalog $25, and the dropship smoke does not call them Hold", () => {
  const root = process.cwd();
  const seed = parseCatalogDocument(
    JSON.parse(readFileSync(path.join(root, "data", "products.json"), "utf8")) as unknown,
  );
  const p02 = seed.products.find((product) => product.ma === "P02");
  const p05 = seed.products.find((product) => product.ma === "P05");
  assert.ok(p02 && p05);
  assert.equal(p02.status, "available");
  assert.equal(p02.priceUsd, 25);
  assert.equal(p05.status, "available");
  assert.equal(p05.priceUsd, 25);
  const overlaid = overlayCustomerStockVoice({
    ...seed,
    products: seed.products.map((product) =>
      product.ma === "P02"
        ? {
            ...product,
            descriptionEn: "Thermos on Hold (photo-check).",
            descriptionVn: "Bình đang Hold.",
          }
        : product,
    ),
  });
  const cleaned = overlaid.products.find((product) => product.ma === "P02");
  assert.ok(cleaned);
  assert.equal(cleaned.status, "available");
  assert.equal(cleaned.priceUsd, 25);
  assert.equal(cleaned.descriptionEn, "Thermos on Hold (photo-check).");
  const offer = productJsonLd(p02).offers as { price?: string };
  assert.equal(offer.price, "25.00");
  const smoke = readFileSync(path.join(root, "scripts", "smoke-dropship.ts"), "utf8");
  assert.equal(smoke.includes("must stay Hold with no USD"), false);
  assert.equal(smoke.includes("Hold JSON-LD must not invent USD"), false);
  assert.equal(smoke.includes("must not flip P02 off Hold"), false);
});
