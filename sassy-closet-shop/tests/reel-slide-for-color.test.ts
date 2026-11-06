import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import {
  clampedReelIndexForColor,
  productGalleryReel,
  reelSlideForColor,
} from "../lib/gallery-reel";
import type { Product, ProductColor, ProductImageAsset } from "../lib/types";

function look(input: {
  ma: string;
  colors: ProductColor[];
  images: ProductImageAsset[];
}): Product {
  return input as Product;
}

const judy: ProductColor = { id: "cp0200", hex: "#111111", name: "Judy", note: "" };
const nick: ProductColor = { id: "cp0201", hex: "#222222", name: "Nick", note: "" };
const stitch: ProductColor = { id: "cp0202", hex: "#333333", name: "Stitch", note: "" };

test("a chip with no photo does not resolve to another finish", () => {
  const reel = productGalleryReel(
    look({
      ma: "P02",
      colors: [judy, nick, stitch],
      images: [
        { src: "/products/P02/cover.jpg", colorId: "cp0201", order: 1 },
        { src: "/products/P02/photo-2.jpg", colorId: "cp0200", order: 2 },
      ],
    }),
  );
  const judySlide = reelSlideForColor(reel, "cp0200");
  const nickSlide = reelSlideForColor(reel, "cp0201");
  assert.equal(reelSlideForColor(reel, null), 0);
  assert.equal(judySlide !== null && reel[judySlide]?.colorId, "cp0200");
  assert.equal(nickSlide !== null && reel[nickSlide]?.colorId, "cp0201");
  assert.equal(reelSlideForColor(reel, "cp0202"), null);
  assert.equal(clampedReelIndexForColor(reel, "cp0202"), 0);
  assert.notEqual(reel[0]?.colorId, "cp0202");
  assert.equal(reel[0]?.src.includes("/products/P02/"), true);
});

test("a shared untagged photo still belongs to a chip with no tagged shot", () => {
  const reel = productGalleryReel(
    look({
      ma: "S04",
      colors: [
        { id: "cs0400", hex: "#aa0000", name: "Red", note: "" },
        { id: "cs0401", hex: "#ffffff", name: "White", note: "" },
      ],
      images: [
        { src: "/products/S04/cover.jpg", colorId: "cs0400", order: 1 },
        { src: "/products/S04/photo-2.jpg", colorId: null, order: 2 },
      ],
    }),
  );
  const white = reelSlideForColor(reel, "cs0401");
  assert.equal(white !== null, true);
  assert.equal(reel[white ?? -1]?.colorId, null);
  assert.equal(reel[white ?? -1]?.src, "/products/S04/photo-2.jpg");
  assert.equal(reel[reelSlideForColor(reel, "cs0400") ?? -1]?.src, "/products/S04/cover.jpg");
});

test("shop seed colors with no photo stay off another finish", () => {
  const catalog = JSON.parse(
    readFileSync(path.join(process.cwd(), "data/products.json"), "utf8"),
  ) as { products: Product[] };
  const expectedMissing = [
    ["P02", "cp0202"],
    ["P03", "cp0301"],
    ["P03", "cp0302"],
    ["P05", "cp0501"],
    ["P05", "cp0503"],
  ] as const;
  for (const [ma, colorId] of expectedMissing) {
    const product = catalog.products.find((row) => row.ma === ma);
    assert.ok(product, ma);
    const reel = productGalleryReel(product);
    assert.equal(reelSlideForColor(reel, colorId), null, `${ma} ${colorId}`);
    assert.equal(reel.some((slide) => slide.colorId === colorId), false);
    if (reel.length > 0) {
      assert.notEqual(reel[clampedReelIndexForColor(reel, colorId)]?.colorId, colorId);
    }
  }
});

test("look card hides the reel when the selected color has no photo", () => {
  const src = readFileSync(path.join(process.cwd(), "components/product-card.tsx"), "utf8");
  assert.match(src, /reelSlideForColor/);
  assert.match(src, /slideForColor === null/);
  assert.match(src, /data-color-photo=\{colorId !== null && slideForColor === null \? "missing" : "shown"\}/);
  assert.match(src, /clampedReelIndexForColor/);
  assert.match(src, /ky-card-reel/);
});
