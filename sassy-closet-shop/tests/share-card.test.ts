import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { formatUsd } from "../lib/format";
import { HOLD_PRICE_LABEL } from "../lib/dropship-copy";
import { renderShareCard } from "../lib/og-card";
import { productJsonLd, productSeo, notFoundSeo } from "../lib/seo";
import {
  cardWithPhoto,
  categorySharePlan,
  productShareCardCopy,
  productSharePlan,
  shareCardVariant,
} from "../lib/share-card";
import { isSelfHostedUrl, loadSharePhoto, sharePhotoFromBytes } from "../lib/share-photo";
import { toShopLook } from "../lib/shop-look";
import { productShareDescription } from "../lib/trust-copy";
import type { Product } from "../lib/types";

function sample(overrides: Partial<Product> = {}): Product {
  return {
    ma: "A15",
    type: "A",
    titleVn: "Áo len hoa xám",
    titleEn: "Heather knit top",
    priceUsd: 23,
    qty: 1,
    status: "available",
    colors: [],
    images: [
      { src: "/products/A15/cover.jpg", colorId: null, order: 1 },
      { src: "/products/A15/photo-2.jpg", colorId: null, order: 2 },
    ],
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "Heather knit top, grey floral.",
    fulfillment: "dropship",
    sourceLink: null,
    ...overrides,
  };
}

function withShopUrl<T>(url: string, run: () => T): T {
  const previous = process.env.NEXT_PUBLIC_SHOP_URL;
  process.env.NEXT_PUBLIC_SHOP_URL = url;
  try {
    return run();
  } finally {
    if (previous === undefined) {
      delete process.env.NEXT_PUBLIC_SHOP_URL;
    } else {
      process.env.NEXT_PUBLIC_SHOP_URL = previous;
    }
  }
}

function read(relative: string): string {
  return readFileSync(path.join(process.cwd(), relative), "utf8");
}

test("unknown mã is never rendered on a share card", () => {
  const plan = productSharePlan(undefined);
  assert.deepEqual(plan, { status: 404 });
  assert.equal(JSON.stringify(plan).includes("Z99"), false);
  assert.deepEqual(categorySharePlan("not-a-slug"), { status: 404 });
});

test("share description uses the catalog price and never invents one", () => {
  const priced = productShareDescription({
    titleEn: "Heather knit top",
    descriptionEn: "Heather knit top, grey floral.",
    priceUsd: 23,
  });
  assert.equal(
    priced,
    "$23 · Heather knit top, grey floral. · Message Sassy Closet on Messenger",
  );
  const local = productShareDescription({
    titleEn: "Heather knit top",
    descriptionEn: "Heather knit top, grey floral.",
    priceUsd: 27,
  });
  assert.equal(local.startsWith("$27 ·"), true);
  const held = productShareDescription({
    titleEn: "Heather knit top",
    descriptionEn: "Heather knit top, grey floral.",
    priceUsd: null,
  });
  assert.equal(
    held,
    "Inbox for price · Heather knit top, grey floral. · Message Sassy Closet on Messenger",
  );
  assert.equal(held.includes("$"), false);
  assert.equal(HOLD_PRICE_LABEL, "Inbox for price");
});

test("seed A15 share copy follows the seed price", () => {
  const rows = JSON.parse(read("data/products.json")) as { products: Product[] };
  const seed = rows.products.find((product) => product.ma === "A15");
  assert.ok(seed);
  assert.equal(seed.priceUsd, 27);
  const description = productShareDescription(seed);
  assert.equal(description.startsWith(`${formatUsd(seed.priceUsd ?? 0)} ·`), true);
  const card = productShareCardCopy(seed);
  assert.equal(card.detail, formatUsd(seed.priceUsd ?? 0));
  assert.equal(card.eyebrow, "A15");
  assert.equal(card.title, "HEATHER KNIT TOP");
  const held = productShareCardCopy({ ...seed, priceUsd: null });
  assert.equal(held.detail, HOLD_PRICE_LABEL);
});

test("a failed photo falls back to a text card", async () => {
  const fields = productShareCardCopy(sample());
  const model = await cardWithPhoto(fields, "/products/A15/cover.jpg", async () => {
    throw new Error("photo failed");
  });
  assert.equal(shareCardVariant(model), "text");
  assert.equal(model.photo, null);
  assert.equal(model.detail, "$23");
});

test("share photos accept jpeg and png and skip self-fetches", async () => {
  const jpeg = new Uint8Array([0xff, 0xd8, 0xff, 0x00, 0x01, 0x02, 0x03, 0x04]);
  const png = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  const webp = new Uint8Array([0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00]);
  assert.equal(sharePhotoFromBytes(jpeg)?.mime, "image/jpeg");
  assert.equal(sharePhotoFromBytes(png)?.mime, "image/png");
  assert.equal(sharePhotoFromBytes(webp), null);
  const missing = await loadSharePhoto("/products/Z99/cover.jpg");
  assert.equal(missing, null);
  const self = new URL("https://preview.example/products/A15/cover.jpg");
  assert.equal(isSelfHostedUrl(self, "https://preview.example/share/m/A15"), true);
  let fetched = false;
  const photo = await loadSharePhoto(self.toString(), {
    requestUrl: "https://preview.example/share/m/A15",
    fetchImpl: async () => {
      fetched = true;
      throw new Error("must not fetch self");
    },
  });
  assert.equal(fetched, false);
  assert.equal(photo?.mime, "image/jpeg");
  assert.ok((photo?.data.byteLength ?? 0) > 8);
});

test("product og image is a versioned png and json-ld lists every photo", () => {
  const look = toShopLook(sample());
  const seo = withShopUrl("https://sassycloset.vercel.app", () => productSeo(look, "ver123"));
  const images = seo.openGraph?.images;
  const image = Array.isArray(images) ? images[0] : undefined;
  assert.equal(
    image && typeof image === "object" && "url" in image ? String(image.url) : "",
    "https://sassycloset.vercel.app/share/m/A15?v=ver123",
  );
  assert.equal(image && typeof image === "object" && "type" in image ? image.type : "", "image/png");
  assert.equal(image && typeof image === "object" && "width" in image ? image.width : 0, 1200);
  assert.equal(image && typeof image === "object" && "height" in image ? image.height : 0, 630);
  assert.match(seo.description ?? "", /^\$23 · Heather knit top, grey floral/);
  const jsonLd = withShopUrl("https://sassycloset.vercel.app", () => productJsonLd(look));
  assert.deepEqual(jsonLd.image, [
    "https://sassycloset.vercel.app/products/A15/cover.jpg",
    "https://sassycloset.vercel.app/products/A15/photo-2.jpg",
  ]);
  assert.equal(JSON.stringify(jsonLd).includes("availability"), false);
  const missing = notFoundSeo();
  assert.equal(missing.robots, null);
  assert.deepEqual(missing.alternates, { canonical: null });
});

test("text share card renders a png", async () => {
  const response = await renderShareCard({
    ...productShareCardCopy(sample()),
    photo: null,
  });
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /image\/png/);
  const bytes = new Uint8Array(await response.arrayBuffer());
  assert.equal(bytes[0], 0x89);
  assert.equal(bytes[1], 0x50);
});

test("pdp gallery and share chip match the r3 contract", () => {
  const gallery = read("components/gallery-peek-roll.tsx");
  assert.equal(gallery.includes("peeking && !reduced"), false);
  assert.equal(gallery.includes("motion-reduce:hidden"), true);
  assert.equal(gallery.includes("calc(100vw - 40px)"), true);
  assert.equal(gallery.includes('fetchPriority={isCenter ? "high" : "low"}'), true);
  const share = read("components/share-look.tsx");
  assert.equal(share.includes("navigator.share"), true);
  assert.equal(share.includes('data-testid="share-look"'), true);
  assert.equal(share.includes("min-h-11"), true);
  const layout = read("app/layout.tsx");
  assert.equal(layout.includes('themeColor: "#fdece6"'), true);
  assert.equal(layout.includes("#111111"), false);
});
