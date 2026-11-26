import assert from "node:assert/strict";
import test from "node:test";
import {
  getSeedDocument,
  overlayCustomerStockVoice,
  overlaySeedHubGalleries,
  overlaySeedPhotoColorTags,
} from "../lib/catalog-store";
import type { CatalogDocument, Product } from "../lib/types";

function rename(document: CatalogDocument, from: string, to: string, patch: Partial<Product> = {}): CatalogDocument {
  return {
    ...document,
    products: document.products.map((product) =>
      product.ma === from ? { ...product, ...patch, ma: to } : product,
    ),
  };
}

test("hub gallery and blank copy follow the canonical mã, and the price stays", () => {
  const seed = getSeedDocument();
  const seedA02 = seed.products.find((product) => product.ma === "A02");
  assert.ok(seedA02);
  assert.ok(seedA02.images.length > 0);
  const price = seedA02.priceUsd;

  for (const spelled of ["A2", "A002", "a02"]) {
    const stored = rename(seed, "A02", spelled, {
      titleEn: "",
      titleVn: "",
      descriptionEn: "",
      descriptionVn: "",
      images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
      priceUsd: price,
    });
    const gallery = overlaySeedHubGalleries(stored);
    const row = gallery.products.find((product) => product.ma === spelled);
    assert.ok(row, spelled);
    assert.equal(row.ma, spelled);
    assert.equal(row.priceUsd, price);
    assert.deepEqual(
      row.images.map((image) => image.src),
      seedA02.images.map((image) => image.src),
      spelled,
    );

    const voice = overlayCustomerStockVoice(stored);
    const titled = voice.products.find((product) => product.ma === spelled);
    assert.ok(titled, spelled);
    assert.equal(titled.priceUsd, price);
    assert.equal(titled.titleEn, seedA02.titleEn, spelled);
    assert.equal(titled.descriptionEn, seedA02.descriptionEn, spelled);
  }

  const exact = overlaySeedHubGalleries(
    rename(seed, "A02", "A02", {
      images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
      priceUsd: price,
    }),
  );
  const a02 = exact.products.find((product) => product.ma === "A02");
  assert.ok(a02);
  assert.equal(a02.priceUsd, price);
  assert.deepEqual(
    a02.images.map((image) => image.src),
    seedA02.images.map((image) => image.src),
  );
});

test("B01 color tags follow a short or padded mã and the price stays", () => {
  const seed = getSeedDocument();
  const seedB01 = seed.products.find((product) => product.ma === "B01");
  assert.ok(seedB01);
  const cover = seedB01.images.find((image) => image.src.endsWith("/cover.jpg"));
  assert.ok(cover);
  assert.ok(cover.colorId);
  const price = seedB01.priceUsd;

  for (const spelled of ["B1", "B001"]) {
    const stored = rename(seed, "B01", spelled, {
      images: seedB01.images.map((image) =>
        image.src.endsWith("/cover.jpg") ? { ...image, colorId: null } : image,
      ),
      priceUsd: price,
    });
    const tagged = overlaySeedPhotoColorTags(stored);
    const row = tagged.products.find((product) => product.ma === spelled);
    assert.ok(row, spelled);
    assert.equal(row.priceUsd, price);
    assert.equal(row.ma, spelled);
    assert.equal(
      row.images.find((image) => image.src.endsWith("/cover.jpg"))?.colorId,
      cover.colorId,
      spelled,
    );
  }
});
