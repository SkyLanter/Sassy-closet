import assert from "node:assert/strict";
import test from "node:test";
import { isColorId, parseProductColor } from "../lib/colors";
import { HUB_SLUG_HEX } from "../lib/kit-catalog";
import { parseCatalogDocument, toCatalogDocumentJson } from "../lib/product-parse";

/**
 * `parseProductColor` fell back to `HUB_SLUG_HEX[id]`. That is a plain-object
 * lookup, so every `Object.prototype` member resolved: the id `constructor`
 * produced the `Object` function as the color's hex. The row then serialized
 * without a `hex` key at all (`JSON.stringify` drops functions), and the admin
 * swatch (`backgroundColor: color.hex`) got a function instead of a color.
 *
 * `isColorId` already refuses these ids, but `parseProductColor` generates a
 * fresh id for an unusable one and keeps the row, so the hex branch is what
 * decides whether the row survives.
 */
test("a prototype key is not a recorded hub hex", () => {
  assert.equal(isColorId("constructor"), true, "the gate still accepts it");
  assert.equal(Object.hasOwn(HUB_SLUG_HEX, "constructor"), false);

  // No recorded hex for this id, so the row is refused rather than minted with
  // a function as its hex: the caller must supply a real hex.
  assert.throws(
    () => parseProductColor({ id: "constructor", name: "Kem" }, "A01", 0),
    /needs a hex value/,
  );
});

test("a real hub slug still takes its recorded hex", () => {
  assert.equal(parseProductColor({ id: "kem" }, "A01", 0).hex, "#F4F0E8");
  assert.equal(parseProductColor({ id: "cham-bi" }, "A01", 0).hex, "#6B6B6B");
});

test("an explicit hex still wins over the recorded one", () => {
  assert.equal(parseProductColor({ id: "kem", hex: "#123456" }, "A01", 0).hex, "#123456");
});

test("a color row with no hex and no recorded slug is refused, never a function", () => {
  for (const id of ["constructor", "toString", "valueOf", "hasOwnProperty"]) {
    assert.equal(Object.hasOwn(HUB_SLUG_HEX, id), false, id);
    assert.throws(
      () => parseProductColor({ id, name: "Kem" }, "A01", 0),
      /needs a hex value/,
      id,
    );
  }
});

test("a catalog color never serializes without its hex", () => {
  const product = {
    ma: "A01",
    type: "A",
    titleEn: "Top",
    titleVn: "",
    priceUsd: 20,
    qty: 1,
    status: "available",
    // `constructor` used to take the `Object` function as its hex, so
    // JSON.stringify dropped the key and the row round-tripped with no color.
    colors: [{ id: "constructor", name: "Kem", note: "" }],
    images: [],
    sizes: [],
    fitCm: {},
    descriptionEn: "",
    descriptionVn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
  assert.throws(
    () =>
      parseCatalogDocument({
        schema: "catalog.v1",
        version: 1,
        siteId: "sassy-closet-shop",
        settings: { announcementLines: ["Sassy Closet"], facebookPageUrl: "https://m.me/x" },
        products: [product],
      }),
    /needs a hex value/,
  );
});

test("a real hub color keeps its recorded hex through a catalog round trip", () => {
  const product = {
    ma: "A01",
    type: "A",
    titleEn: "Top",
    titleVn: "",
    priceUsd: 20,
    qty: 1,
    status: "available",
    colors: [{ id: "kem", name: "Kem", note: "" }],
    images: [{ src: "/products/A01/cover.jpg", colorId: "kem", order: 1 }],
    sizes: [],
    fitCm: {},
    descriptionEn: "",
    descriptionVn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
  const parsed = parseCatalogDocument({
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    settings: { announcementLines: ["Sassy Closet"], facebookPageUrl: "https://m.me/x" },
    products: [product],
  });
  const colors = JSON.parse(toCatalogDocumentJson(parsed)).products[0].colors;
  assert.deepEqual(colors, [{ id: "kem", hex: "#F4F0E8", name: "Kem", note: "" }]);
});
