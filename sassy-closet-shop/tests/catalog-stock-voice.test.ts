import assert from "node:assert/strict";
import test from "node:test";
import { getSeedDocument, overlayCustomerStockVoice } from "../lib/catalog-store";
import type { CatalogDocument, Product } from "../lib/types";

const BLOB_A02_TITLE = "Polka-dot top";
const BLOB_A02_DESCRIPTION = "Polka-dot collar puff-sleeve top with a grey wool body.";

function withProduct(document: CatalogDocument, ma: string, patch: Partial<Product>): CatalogDocument {
  return {
    ...document,
    products: document.products.map((product) => (product.ma === ma ? { ...product, ...patch } : product)),
  };
}

test("stored Blob title and description stay; seed fills a blank and leaves price", () => {
  const seed = getSeedDocument();
  const seedA02 = seed.products.find((product) => product.ma === "A02");
  assert.ok(seedA02);
  assert.equal(seedA02.titleEn, "Polka-dot dress");
  assert.equal(seedA02.descriptionEn, "Polka-dot collar puff-sleeve dress with a grey wool body.");
  assert.equal(seedA02.priceUsd, 23);

  const stored = withProduct(seed, "A02", {
    titleEn: BLOB_A02_TITLE,
    descriptionEn: BLOB_A02_DESCRIPTION,
    priceUsd: 23,
  });
  const overlaid = overlayCustomerStockVoice(stored);
  const a02 = overlaid.products.find((product) => product.ma === "A02");
  assert.ok(a02);
  assert.equal(a02.titleEn, BLOB_A02_TITLE);
  assert.equal(a02.descriptionEn, BLOB_A02_DESCRIPTION);
  assert.equal(a02.titleVn, seedA02.titleVn);
  assert.equal(a02.descriptionVn, seedA02.descriptionVn);
  assert.equal(a02.priceUsd, 23);
  assert.equal(a02.titleEn.includes("dress"), false);
  assert.equal(a02.descriptionEn.includes("dress"), false);
  assert.equal(stored.products.find((product) => product.ma === "A02")?.titleEn, BLOB_A02_TITLE);

  const blanked = withProduct(stored, "A02", {
    titleEn: "  ",
    descriptionVn: "",
  });
  const filled = overlayCustomerStockVoice(blanked).products.find((product) => product.ma === "A02");
  assert.ok(filled);
  assert.equal(filled.titleEn, seedA02.titleEn);
  assert.equal(filled.descriptionEn, BLOB_A02_DESCRIPTION);
  assert.equal(filled.titleVn, seedA02.titleVn);
  assert.equal(filled.descriptionVn, seedA02.descriptionVn);
  assert.equal(filled.priceUsd, 23);
});

test("extra mãs still blank ops descriptions and keep a real one", () => {
  const seed = getSeedDocument();
  const seedA01 = seed.products.find((product) => product.ma === "A01");
  assert.ok(seedA01);
  const ops = overlayCustomerStockVoice({
    ...seed,
    products: [
      ...seed.products,
      {
        ...seedA01,
        ma: "A99",
        titleEn: "Top",
        titleVn: "Áo",
        descriptionEn: "One unique top. Message A99 to order — sourced after you inbox.",
        descriptionVn: "Áo độc bản. Nhắn tin A99 để đặt.",
      },
    ],
  });
  const a99 = ops.products.find((product) => product.ma === "A99");
  assert.equal(a99?.titleEn, "Top");
  assert.equal(a99?.descriptionEn, "");
  assert.equal(a99?.descriptionVn, "");

  const kept = overlayCustomerStockVoice({
    ...seed,
    products: [
      ...seed.products,
      {
        ...seedA01,
        ma: "A99",
        titleEn: "Soft knit",
        titleVn: "Áo mềm",
        descriptionEn: "Soft knit.",
        descriptionVn: "Áo mềm.",
      },
    ],
  });
  const real = kept.products.find((product) => product.ma === "A99");
  assert.equal(real?.titleEn, "Soft knit");
  assert.equal(real?.descriptionEn, "Soft knit.");
  assert.equal(real?.descriptionVn, "Áo mềm.");
});
