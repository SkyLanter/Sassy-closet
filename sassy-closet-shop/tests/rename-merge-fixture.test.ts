import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { mergeProductColors } from "../lib/admin-ops";
import { mergeCatalogDocuments } from "../lib/catalog-merge";
import { asCatalogDocument, parseCatalogDocument } from "../lib/product-parse";
import type { Product } from "../lib/types";

const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as unknown,
);

function twoToneFrom(base: Product, ma: string): Product {
  return {
    ...base,
    ma,
    colors: [
      { id: "cblackcolor01", hex: "#111111", name: "Black", note: "" },
      { id: "ccamelcolor01", hex: "#B08968", name: "Camel", note: "" },
    ],
    images: [
      { src: "/products/A01/cover.jpg", colorId: "cblackcolor01", order: 1 },
      { src: "/products/A01/alt.jpg", colorId: "ccamelcolor01", order: 2 },
    ],
  };
}

test("a later duplicate mã does not receive the color merge", () => {
  const a01 = seed.products.find((product) => product.ma === "A01");
  assert.ok(a01);
  assert.equal(
    seed.products.some((product) => product.ma === "A03"),
    true,
    "A03 is already a seed row",
  );
  const duplicated = [...seed.products, twoToneFrom(a01, "A03")];
  const hitReal = mergeProductColors(duplicated, "A03", "cblackcolor01", "ccamelcolor01");
  assert.equal(hitReal.ok, false);
  if (hitReal.ok) {
    return;
  }
  assert.match(hitReal.error, /Both colors must exist/);
});

test("color merge retags the row that actually has those colors", () => {
  const a01 = seed.products.find((product) => product.ma === "A01");
  assert.ok(a01);
  const catalog = seed.products.map((product) =>
    product.ma === "A01" ? twoToneFrom(a01, "A01") : product,
  );
  const merged = mergeProductColors(catalog, "A01", "cblackcolor01", "ccamelcolor01");
  assert.equal(merged.ok, true);
  if (!merged.ok) {
    return;
  }
  const row = merged.products.find((product) => product.ma === "A01");
  assert.ok(row);
  assert.deepEqual(
    row.colors.map((color) => color.id),
    ["cblackcolor01"],
  );
  assert.ok(row.images.every((image) => image.colorId === "cblackcolor01"));
  assert.equal(row.priceUsd, a01.priceUsd);
});

test("catalog merge adds a mã the seed does not already contain", () => {
  const a01 = seed.products[0];
  assert.ok(a01);
  assert.equal(
    seed.products.some((product) => product.ma === "A99"),
    false,
  );
  const incoming = asCatalogDocument(
    [
      {
        ...a01,
        ma: "A99",
        status: "hold",
        priceUsd: null,
        colors: [],
        images: [],
        sizes: [],
        sourceLink: null,
      },
    ],
    seed.settings,
  );
  const merged = mergeCatalogDocuments(seed, incoming);
  assert.equal(merged.products.length, seed.products.length + 1);
  assert.equal(
    merged.products.some((product) => product.ma === "A99"),
    true,
  );
  const kept = merged.products.find((product) => product.ma === "A01");
  assert.equal(kept?.priceUsd, a01.priceUsd);
  assert.equal(kept?.status, a01.status);
});
