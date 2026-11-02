import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { storedSizeText } from "../lib/size-guide";
import { toShopLook } from "../lib/shop-look";
import type { Product } from "../lib/types";

function sample(sizes: Product["sizes"]): Product {
  return {
    ma: "A01",
    type: "A",
    titleVn: "Áo len puppy",
    titleEn: "Puppy cardigan",
    priceUsd: 27,
    qty: 1,
    status: "available",
    colors: [],
    images: [],
    sizes,
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

test("size guide repeats the size text already on the look", () => {
  const look = toShopLook(sample(["L", "S", "M"]));
  assert.deepEqual(storedSizeText(look.sizes), ["S", "M", "L"]);
  assert.equal(storedSizeText(["M"]).join(" "), "M");
  assert.deepEqual(storedSizeText([]), []);
  assert.deepEqual(storedSizeText(["  ", ""]), []);
});

test("size guide does not fill letters the look does not have", () => {
  const onlyMedium = storedSizeText(toShopLook(sample(["M"])).sizes);
  assert.deepEqual(onlyMedium, ["M"]);
  const none = storedSizeText(toShopLook(sample([])).sizes);
  assert.deepEqual(none, []);
});

test("sell PDP size guide renders stored sizes and stays off an empty row", () => {
  const guide = readFileSync(path.join(process.cwd(), "components/size-guide.tsx"), "utf8");
  const helper = readFileSync(path.join(process.cwd(), "lib/size-guide.ts"), "utf8");
  const look = readFileSync(path.join(process.cwd(), "components/product-look.tsx"), "utf8");
  assert.match(guide, /storedSizeText\(sizes\)/);
  assert.match(guide, /data-testid="size-guide"/);
  assert.match(guide, /lines\.length === 0/);
  assert.equal(guide.includes("ASIA_SIZE_LETTERS"), false);
  assert.equal(helper.includes("ASIA_SIZE_LETTERS"), false);
  assert.match(look, /<SizeGuide sizes=\{product\.sizes\} \/>/);
});
