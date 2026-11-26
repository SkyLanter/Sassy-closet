import assert from "node:assert/strict";
import test from "node:test";
import { fieldsFromProduct, saveProductInCatalog } from "../lib/admin-ops";
import { getSeedDocument } from "../lib/catalog-store";
import { productGalleryReel } from "../lib/gallery-reel";
import { applyRecordedHubColors, hubColorLocked, recordedHubSlugs } from "../lib/hub-colors";
import { applyHubColorNames } from "../lib/hub-import";
import { toShopLook } from "../lib/shop-look";
import type { Product } from "../lib/types";

// P01 and P04 carry one recorded hub color in the seed. A live row can be stored
// with a short or padded spelling of the same mã; it is still that hub mã.
const RECORDED: ReadonlyArray<[string, string]> = [
  ["P01", "hoa"],
  ["P04", "kem"],
];

function spellings(ma: string): string[] {
  const letter = ma[0] ?? "";
  const digits = ma.slice(1);
  return [ma, `${letter}0${digits}`, `${letter}${Number(digits)}`, ma.toLowerCase()];
}

function seedRow(ma: string): Product {
  const row = getSeedDocument().products.find((product) => product.ma === ma);
  assert.ok(row, ma);
  return row;
}

/** The live row keeps its recorded hub chip and the photo tagged to it. */
function storedHubRow(ma: string, slug: string): Product {
  const row = seedRow(ma);
  return {
    ...row,
    colors: [{ id: slug, hex: "#C4A484", name: "Hoa", note: "" }],
    images: [
      { src: `https://store.public.blob.vercel-storage.com/${ma.toLowerCase()}/cover.jpg`, colorId: slug, order: 1 },
    ],
  };
}

test("a short or padded hub mã still reports its recorded color", () => {
  for (const [ma, slug] of RECORDED) {
    assert.deepEqual(recordedHubSlugs(ma), [slug], ma);
    for (const spelled of spellings(ma)) {
      assert.equal(hubColorLocked(spelled), true, `locked ${spelled}`);
      assert.deepEqual(recordedHubSlugs(spelled), [slug], `recorded ${spelled}`);
    }
  }
  // Extra mãs stay unlocked and keep their own colors.
  assert.equal(hubColorLocked("A03"), false);
  assert.deepEqual(recordedHubSlugs("A03"), []);
});

test("a recorded hub chip and its photo tag survive a short or padded mã", () => {
  for (const [ma, slug] of RECORDED) {
    for (const spelled of spellings(ma)) {
      const row = { ...storedHubRow(ma, slug), ma: spelled };
      const applied = applyRecordedHubColors(row);
      assert.deepEqual(
        applied.colors.map((color) => color.id),
        [slug],
        `color kept on ${spelled}`,
      );
      assert.deepEqual(
        applied.images.map((image) => image.colorId),
        [slug],
        `photo tag kept on ${spelled}`,
      );
      assert.equal(applied.ma, spelled, "the stored spelling is left as written");

      const look = toShopLook(applyHubColorNames([row])[0] as Product);
      assert.deepEqual(look.colors.map((color) => color.id), [slug], `look color on ${spelled}`);
      assert.equal(look.images.length, 1, `look photo on ${spelled}`);
      assert.deepEqual(
        productGalleryReel(look).map((slide) => slide.colorId),
        [slug],
        `reel slide on ${spelled}`,
      );
    }
  }
});

test("an unchanged admin save on a short or padded hub mã keeps the chip", () => {
  for (const [ma, slug] of RECORDED) {
    const letter = ma[0] ?? "";
    const digits = ma.slice(1);
    for (const spelled of [`${letter}0${digits}`, `${letter}${Number(digits)}`, ` ${ma.toLowerCase()} `]) {
      const row = { ...storedHubRow(ma, slug), ma: spelled };
      const saved = saveProductInCatalog([row], row.ma, fieldsFromProduct(row));
      assert.equal(saved.ok, true, `${row.ma}: ${saved.ok ? "" : saved.error}`);
      if (!saved.ok) {
        continue;
      }
      const after = saved.products[0];
      assert.ok(after);
      assert.deepEqual(after.colors.map((color) => color.id), [slug], `saved color on ${row.ma}`);
      assert.deepEqual(after.images.map((image) => image.colorId), [slug], `saved tag on ${row.ma}`);
    }
  }
});
