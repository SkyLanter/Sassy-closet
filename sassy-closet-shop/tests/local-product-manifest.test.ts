import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import localProductFiles from "../data/local-product-files.json";
import { overlayCleanedExtraCovers } from "../lib/catalog-store";
import type { CatalogDocument } from "../lib/types";

const V02_BLOB =
  "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/products/V02/cover.jpg";

test("product photos use the build-time file list", () => {
  const store = readFileSync(path.join(process.cwd(), "lib", "catalog-store.ts"), "utf8");
  assert.equal(store.includes("existsSync"), false);
  assert.equal(store.includes("local-product-files.json"), true);

  const files = new Set(localProductFiles);
  for (const rel of [
    "A15/cover.jpg",
    "A15/photo-2.jpg",
    "S03/cover.jpg",
    "O03/cover.jpg",
    "O03/photo-3.jpg",
    "P03/cover.jpg",
    "P03/photo-2.jpg",
    "P03/photo-3.jpg",
    "V01/cover.jpg",
    "D02/cover.jpg",
    "D02/photo-2.jpg",
    "A16/cover.jpg",
    "D04/cover.jpg",
    "S09/cover.jpg",
  ]) {
    assert.equal(files.has(rel), true, rel);
  }
  for (const rel of [
    "V02/cover.jpg",
    "S03/photo-2.jpg",
    "S03/photo-3.jpg",
    "O03/photo-2.jpg",
    "D02/photo-3.jpg",
    "D02/photo-4.jpg",
    "D02/photo-5.jpg",
    "B03/photo-3.jpg",
    "A10/photo-6.jpg",
  ]) {
    assert.equal(files.has(rel), false, rel);
  }

  const doc = overlayCleanedExtraCovers({
    products: [
      {
        ma: "V01",
        images: [
          {
            src: "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/products/V01/cover.jpg",
            colorId: null,
            order: 1,
          },
        ],
      },
      {
        ma: "V02",
        images: [{ src: V02_BLOB, colorId: null, order: 1 }],
      },
      {
        ma: "B03",
        images: [{ src: "/products/B03/cover.jpg", colorId: null, order: 1 }],
      },
    ],
  } as CatalogDocument);

  assert.equal(doc.products.find((product) => product.ma === "V01")?.images[0]?.src, "/products/V01/cover.jpg");
  assert.equal(doc.products.find((product) => product.ma === "V02")?.images[0]?.src, V02_BLOB);
  assert.equal(doc.products.find((product) => product.ma === "B03")?.images[0]?.src, "/products/B03/cover.jpg");
});
