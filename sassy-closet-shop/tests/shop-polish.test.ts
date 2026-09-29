import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import {
  messengerAskHref,
  messengerAskSentence,
  messengerSizeAskHref,
  messengerSizeAskSentence,
} from "../lib/messenger-ask";
import { messengerHref } from "../lib/messenger";
import { lookPhotoAlt } from "../lib/photo-alt";
import { productSeo } from "../lib/seo";
import { shopLookPayloadLeak, shopMeasurements, toShopLook } from "../lib/shop-look";
import { collectShopSizes } from "../lib/shop-sizes";
import { SHOW_TRUST_STRIP, TRUST_PAY_LINE, TRUST_SHIP_LINE } from "../lib/trust-strip";
import type { Product } from "../lib/types";

function sample(fit = emptyFitCm()): Product {
  return {
    ma: "A15",
    type: "A",
    titleVn: "Áo",
    titleEn: "Puppy cardigan",
    priceUsd: 28,
    qty: 1,
    status: "available",
    colors: [],
    images: [],
    sizes: ["M", "S"],
    fitCm: fit,
    descriptionVn: "",
    descriptionEn: "Soft cardigan",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

test("trust strip stays off and does not name a shipping price", () => {
  assert.equal(SHOW_TRUST_STRIP, false);
  assert.match(TRUST_PAY_LINE, /Zelle \(Thang Tien Huynh\)/);
  assert.match(TRUST_SHIP_LINE, /Ship trong Mỹ sau khi nhận Zelle/);
  assert.equal(/\$\d/.test(TRUST_PAY_LINE + TRUST_SHIP_LINE), false);
  const footer = readFileSync(path.join(process.cwd(), "components/footer.tsx"), "utf8");
  assert.equal(footer.includes("TrustStrip"), true);
  assert.equal(/Zelle|Thang Tien Huynh/.test(footer), false);
});

test("product message keeps a direct m.me link and fills the Vietnamese ask", () => {
  const page = "https://m.me/61594312648057";
  assert.equal(messengerHref(page).includes("text="), false);
  assert.equal(
    messengerAskSentence("A15", "M", "Đen"),
    "Chị ơi, còn A15 size M màu Đen không ạ?",
  );
  assert.equal(messengerAskSentence("A15", null, null), "Chị ơi, còn A15 không ạ?");
  assert.equal(messengerAskSentence("S10", "S", null), "Chị ơi, còn S10 size S không ạ?");
  assert.equal(messengerAskSentence("D03", null, "Hồng"), "Chị ơi, còn D03 màu Hồng không ạ?");
  const href = messengerAskHref(page, "A15", "M", "Đen");
  const url = new URL(href);
  assert.equal(url.origin + url.pathname, "https://m.me/61594312648057");
  assert.equal(url.searchParams.get("text"), "Chị ơi, còn A15 size M màu Đen không ạ?");
});

test("size ask leaves the measurements blank and names a selected size", () => {
  const page = "https://m.me/61594312648057";
  assert.equal(
    messengerSizeAskSentence("A01", null, null),
    "Chị ơi, em cao ___ cm, nặng ___ kg. A01 em nên lấy size nào ạ?",
  );
  assert.equal(
    messengerSizeAskSentence("A01", "M", null),
    "Chị ơi, em cao ___ cm, nặng ___ kg. A01 em nên lấy size nào ạ? Size M.",
  );
  assert.equal(
    messengerSizeAskSentence("A01", "M", "Purple"),
    "Chị ơi, em cao ___ cm, nặng ___ kg. A01 em nên lấy size nào ạ? Size M. Màu Purple.",
  );
  const href = messengerSizeAskHref(page, "A01", null, null);
  const url = new URL(href);
  assert.equal(url.origin + url.pathname, "https://m.me/61594312648057");
  assert.equal(
    url.searchParams.get("text"),
    "Chị ơi, em cao ___ cm, nặng ___ kg. A01 em nên lấy size nào ạ?",
  );
});

test("product share image stays the branded 1200×630 card", () => {
  const previous = process.env.NEXT_PUBLIC_SHOP_URL;
  process.env.NEXT_PUBLIC_SHOP_URL = "https://example.test";
  try {
    const look = toShopLook({
      ...sample(),
      images: [{ src: "https://litter.catbox.moe/dead.jpg", colorId: null, order: 1 }],
    });
    const images = productSeo(look).openGraph?.images;
    const image = Array.isArray(images) ? images[0] : undefined;
    assert.equal(image && typeof image === "object" && "url" in image ? String(image.url) : "", "https://example.test/share/m/A15");
    assert.equal(image && typeof image === "object" && "width" in image ? image.width : 0, 1200);
    assert.equal(image && typeof image === "object" && "height" in image ? image.height : 0, 630);
  } finally {
    if (previous === undefined) {
      delete process.env.NEXT_PUBLIC_SHOP_URL;
    } else {
      process.env.NEXT_PUBLIC_SHOP_URL = previous;
    }
  }
});

test("photo alt uses the title, mã, and catalog color only", () => {
  assert.equal(
    lookPhotoAlt({ title: "PUPPY CARDIGAN", ma: "A15", color: "Đen", index: 1 }),
    "PUPPY CARDIGAN, Mã A15, Đen, photo 1",
  );
  assert.equal(lookPhotoAlt({ title: "A15", ma: "A15" }), "Mã A15");
});

test("fit notes use stored centimeters and stay out of the ops payload", () => {
  const empty = toShopLook(sample());
  assert.equal(empty.measurements, null);
  assert.equal(shopLookPayloadLeak(empty), null);
  assert.equal(JSON.stringify(empty).includes('"fitCm"'), false);

  const measured = toShopLook(sample({ bustChestCm: 88, waistCm: null, lengthCm: 60 }));
  assert.deepEqual(measured.measurements, { bustChestCm: 88, waistCm: null, lengthCm: 60 });
  assert.equal(shopMeasurements(sample().fitCm), null);
  assert.equal(JSON.stringify(measured).includes('"fitCm"'), false);
  assert.equal(shopLookPayloadLeak(measured), null);
});

test("size filters list only letters already on the looks", () => {
  assert.deepEqual(
    collectShopSizes([{ sizes: ["L", "S"] }, { sizes: ["M", "S"] }, { sizes: [] }]),
    ["S", "M", "L"],
  );
  assert.deepEqual(collectShopSizes([{ sizes: [] }]), []);
});
