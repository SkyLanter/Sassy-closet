import { createHash } from "node:crypto";
import { existsSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { saveProductInCatalog } from "../lib/admin-ops";
import {
  applyRecordedHubColors,
  bindColorId,
  hubColorLocked,
  recordedHubSlugs,
} from "../lib/hub-colors";
import { isColorId } from "../lib/colors";
import { parseCatalogDocument } from "../lib/product-parse";
import { assignSlideColor, moveLinkedSlide } from "../lib/image-order";
import { overlaySeedHubGalleries } from "../lib/catalog-store";
import { applyHubColorNames } from "../lib/hub-import";
import { firstReelIndexForColor, productGalleryReel } from "../lib/gallery-reel";
import { coverSrcForColor, imagesForColor, ownMaImages, srcBelongsToMa } from "../lib/product-media";
import type { Product } from "../lib/types";

function fail(message: string): never {
  throw new Error(message);
}

const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as unknown,
);

if (!isColorId("kem") || !isColorId("cham-bi") || !isColorId("cblackcolor01")) {
  fail("kem / cham-bi / generated c-ids must parse as color ids");
}
if (isColorId("do-not") || isColorId("unassigned")) {
  fail("Invented slugs must not look like color ids");
}

const a01 = seed.products.find((product) => product.ma === "A01");
if (!a01) {
  fail("A01 missing");
}
// A01's colors are the hub-recorded Yellow/Purple (seller SKU truth):
// every color id must be real with a hex, never an invented slug.
if (a01.colors.map((color) => color.name).sort().join(",") !== "Purple,Yellow") {
  fail("A01 keeps the hub-recorded Yellow/Purple colors");
}
if (a01.colors.length === 0 || !a01.colors.every((color) => isColorId(color.id) && color.hex)) {
  fail("A01 must carry its recorded colors with hexes");
}
const a01ColorIds = new Set(a01.colors.map((color) => color.id));
const a01FirstColor = a01.colors[0]!.id;
if (a01.images.some((image) => image.src.includes(".svg"))) {
  fail("A01 must not use an SVG placeholder");
}
// Cover and photo-2 bind onto colors that exist on this mã.
if (a01.images[0]?.src !== "/products/A01/cover.jpg" || !a01ColorIds.has(a01.images[0]?.colorId ?? "")) {
  fail("A01 cover must bind a recorded color on this mã");
}
if (a01.images[1]?.src !== "/products/A01/photo-2.jpg" || !a01ColorIds.has(a01.images[1]?.colorId ?? "")) {
  fail("A01 photo-2 must bind a recorded color on this mã");
}
if (a01.images[0]?.order !== 1 || a01.images[1]?.order !== 2) {
  fail("A01 photos must stay order 1 then 2");
}
const a01CoverPath = path.join(process.cwd(), "public", "products", "A01", "cover.jpg");
if (existsSync(path.join(process.cwd(), "public", "products", "A01", "cover.svg"))) {
  fail("Delete the AI cover.svg for A01");
}
// Photos hydrate from Blob at build and are not in git — validate the file
// only when it exists locally.
if (existsSync(a01CoverPath)) {
  if (statSync(a01CoverPath).size < 300_000) {
    fail("A01 cover.jpg is too small to be the real intake photo");
  }
  const a01Jpeg = readFileSync(a01CoverPath);
  if (a01Jpeg[0] !== 0xff || a01Jpeg[1] !== 0xd8) {
    fail("A01 cover must be a JPEG");
  }
}

const p04seed = seed.products.find((product) => product.ma === "P04");
if (!p04seed) {
  fail("P04 missing");
}
const remapped = applyRecordedHubColors({
  ...p04seed,
  colors: [
    { id: "ckemivory01", hex: "#F4F0E8", name: "Kem", note: "" },
    { id: "cxanhnavy01", hex: "#1C2A4A", name: "Xanh", note: "" },
  ],
  images: [{ src: "/products/P04/cover.jpg", colorId: "ckemivory01", order: 1 }],
});
if (remapped.colors.map((color) => color.id).join(",") !== "kem") {
  fail("Leftover generated ids must remap onto recorded hub slugs");
}
if (remapped.images[0]?.colorId !== "kem") {
  fail("A tagged leftover id must follow the remap onto kem");
}

const tagged = saveProductInCatalog(seed.products, "A01", {
  titleEn: a01.titleEn,
  titleVn: a01.titleVn,
  descriptionEn: a01.descriptionEn,
  descriptionVn: a01.descriptionVn,
  status: a01.status,
  priceUsd: a01.priceUsd,
  colors: a01.colors,
  images: [
    { src: "/products/A01/cover.jpg", colorId: a01FirstColor, order: 1 },
    { src: "/products/A01/cover.jpg", colorId: null, order: 2 },
  ],
});
if (!tagged.ok) {
  fail(tagged.error);
}
const savedA01 = tagged.products.find((product) => product.ma === "A01");
if (!savedA01 || savedA01.images[0]?.colorId !== a01FirstColor || savedA01.images[1]?.colorId !== null) {
  fail("A01 must store a recorded color id or null — not an invented slug");
}

const stolen = saveProductInCatalog(seed.products, "A01", {
  titleEn: a01.titleEn,
  titleVn: a01.titleVn,
  descriptionEn: a01.descriptionEn,
  descriptionVn: a01.descriptionVn,
  status: a01.status,
  priceUsd: a01.priceUsd,
  colors: a01.colors,
  images: [{ src: "/products/A01/cover.jpg", colorId: "do", order: 1 }],
});
if (!stolen.ok) {
  fail(stolen.error);
}
if (stolen.products.find((product) => product.ma === "A01")?.images[0]?.colorId !== null) {
  fail("A01 must drop colorId do — that slug is not on this mã");
}

const k01 = seed.products.find((product) => product.ma === "K01");
if (!k01) {
  fail("K01 missing");
}
if (recordedHubSlugs("K01").length !== 0 || !hubColorLocked("K01")) {
  fail("K01 stays locked with empty recorded slugs");
}
// An invented hub slug on K01 must not stick — the seed's own colors are untouched.
const inventedDen = applyRecordedHubColors({
  ...k01,
  colors: [{ id: "den", hex: "#111111", name: "Đen", note: "" }],
  images: [{ src: "/products/K01/cover.jpg", colorId: "den", order: 1 }],
});
if (inventedDen.colors.length !== 0 || inventedDen.images[0]?.colorId !== null) {
  fail("K01 must not keep an invented den bind");
}

const h01Seller = applyRecordedHubColors({
  ...seed.products.find((product) => product.ma === "H01")!,
  colors: [
    { id: "ch0100", hex: "#E8B4B8", name: "Pink", note: "" },
    { id: "ch0101", hex: "#7A9BB8", name: "Blue", note: "" },
    { id: "ch0102", hex: "#722F37", name: "Wine", note: "" },
  ],
  images: [{ src: "/products/H01/cover.jpg", colorId: "ch0100", order: 1 }],
});
if (h01Seller.colors.map((color) => color.name).join(",") !== "Pink,Blue,Wine") {
  fail("H01 must keep seller Pink/Blue/Wine — do not wipe recorded hair colors");
}
if (h01Seller.images[0]?.colorId !== "ch0100") {
  fail("H01 Pink bind must stay on the photo");
}

// Gallery invariant across the whole catalog: every image lives under its
// mã's /products/ folder, and every color bind points at a color on that mã.
for (const product of seed.products) {
  const colorIds = new Set(product.colors.map((color) => color.id));
  for (const image of product.images) {
    const src = image.src.split("?")[0] ?? "";
    if (!src.startsWith(`/products/${product.ma}/`)) {
      fail(`${product.ma} image escapes its /products/ folder: ${src}`);
    }
    if (image.colorId !== null && !colorIds.has(image.colorId)) {
      fail(`${product.ma} image binds unknown color ${image.colorId}`);
    }
  }
}

// When pack photos exist on disk (Blob-hydrated), they must be real,
// uniquely-byte'd JPEGs — never a cloned fake peek.
for (const product of seed.products) {
  const hashes = new Set<string>();
  for (const image of product.images) {
    const file = image.src.split("?")[0] ?? "";
    if (!file.startsWith("/products/")) {
      continue;
    }
    const disk = path.join(process.cwd(), "public", file);
    if (!existsSync(disk)) {
      continue; // not hydrated locally — Blob serves it in production
    }
    const buf = readFileSync(disk);
    if (buf[0] !== 0xff || buf[1] !== 0xd8) {
      fail(`${product.ma} ${file} must be a JPEG`);
    }
    if (buf.length < 80_000) {
      fail(`${product.ma} ${file} is too small to be a real intake photo`);
    }
    const hash = createHash("md5").update(buf).digest("hex");
    if (hashes.has(hash)) {
      fail(`${product.ma} must not clone the same JPEG as a fake peek`);
    }
    hashes.add(hash);
  }
}

const p05 = seed.products.find((product) => product.ma === "P05");
if (!p05 || p05.status !== "available" || p05.priceUsd !== 28) {
  fail("P05 keeps its $28 sell");
}
// Cross-check the seed against the hub's recorded character colors.
if (p05.colors.map((color) => color.name).join(",") !== "Peanuts,Hello Kitty,My Melody,Cinnamoroll,Kuromi") {
  fail("P05 keeps the hub-recorded character colors");
}

const p02 = seed.products.find((product) => product.ma === "P02");
if (!p02 || p02.status !== "available" || p02.priceUsd !== 28) {
  fail("P02 keeps its $28 sell");
}

const a02 = seed.products.find((product) => product.ma === "A02");
if (!a02 || a02.colors[0]?.name !== "Off-white") {
  fail("A02 keeps the hub-recorded Off-white — do not rename");
}
if (!srcBelongsToMa("/products/A02/cover.jpg", "A02") || srcBelongsToMa("/products/A01/cover.jpg", "A02")) {
  fail("A02 folder filter must keep A02 files and drop A01");
}
if (!srcBelongsToMa("/products/A04/cover.jpg", "A03")) {
  fail("Rename extras may keep the previous folder so thumbs do not 404");
}
if (ownMaImages({ ma: "A03", colors: [], images: [] }).length !== 0) {
  fail("A03 with no images has no shop photos");
}
if (ownMaImages(a01).length === 0) {
  fail("A01 must keep its own listing photos");
}
// A02 has no recorded hub slugs: a foreign kem slug must drop, Off-white stays.
const remappedA02 = applyHubColorNames([
  {
    ...a02,
    colors: [...a02.colors, { id: "kem", hex: "#F4F0E8", name: "Kem", note: "" }],
    images: a02.images,
  },
])[0];
if (!remappedA02 || remappedA02.colors.some((color) => color.id === "kem")) {
  fail("A02 must drop the foreign kem slug — Off-white stays");
}
if (!remappedA02.colors.some((color) => color.name === "Off-white")) {
  fail("A02 keeps Off-white through the hub color pass");
}
if (remappedA02.images.some((image) => image.src.includes("/products/A01/"))) {
  fail("Stale A02 must drop A01 files");
}
const leakedLive = overlaySeedHubGalleries({
  ...seed,
  products: seed.products.map((product) =>
    product.ma === "A02"
      ? { ...product, colors: a01.colors, images: a01.images }
      : product,
  ),
});
const repairedA02 = leakedLive.products.find((product) => product.ma === "A02");
if (!repairedA02 || repairedA02.images.some((image) => image.src.includes("/products/A01/"))) {
  fail("Live overlay must strip A01 files from A02");
}
if (!repairedA02.images.some((image) => image.src === "/products/A02/cover.jpg")) {
  fail("Empty A02 after drop must refill seed photos");
}
const aiCoverLive = overlaySeedHubGalleries({
  ...seed,
  products: seed.products.map((product) =>
    product.ma === "A01"
      ? {
          ...product,
          images: [
            {
              src: "https://blob.vercel-storage.com/ai-camisole.jpg",
              colorId: "kem",
              order: 1,
            },
          ],
        }
      : product,
  ),
});
const repairedA01 = aiCoverLive.products.find((product) => product.ma === "A01");
if (repairedA01?.images[0]?.src !== "/products/A01/cover.jpg") {
  fail("Hub overlay must force the real intake cover, never a Blob AI file");
}
if (coverSrcForColor(a02, "kem") !== undefined || imagesForColor(a02, "kem").length !== 0) {
  fail("A02 has no kem — honest empty, never A01 cover");
}

if (bindColorId(a01.colors, a01FirstColor) !== a01FirstColor || bindColorId(a01.colors, "hong") !== null) {
  fail("bindColorId only accepts an id already on that mã");
}

const colorView = imagesForColor(savedA01!, a01FirstColor);
if (colorView.length !== 2) {
  fail("Color view is tagged ∪ untagged on this mã");
}

const extra: Product = {
  ...a01,
  ma: "A03",
  type: "A",
  colors: [{ id: "cblackcolor01", hex: "#111111", name: "Black", note: "" }],
  images: [{ src: "/products/A01/cover.jpg", colorId: "cblackcolor01", order: 1 }],
};
if (hubColorLocked("A03")) {
  fail("A03 is not a hub mã — media lock is the ten only");
}
if (applyRecordedHubColors(extra).colors[0]?.id !== "cblackcolor01") {
  fail("Do not rewrite extra-mã colors onto hub slugs");
}

const linked = [
  { src: "/a.jpg", colorId: "kem", order: 1 },
  { src: "/b.jpg", colorId: null, order: 2 },
  { src: "/c.jpg", colorId: "kem", order: 3 },
];
const moved = moveLinkedSlide(linked, "kem", 0, 1);
if (moved[0]?.src !== "/c.jpg" || moved[2]?.src !== "/a.jpg" || moved[1]?.src !== "/b.jpg") {
  fail("moveLinkedSlide must swap only this color’s tagged rows");
}
const assigned = assignSlideColor(linked, "/b.jpg", "kem", null);
if (assigned[1]?.colorId !== "kem") {
  fail("assignSlideColor must tag an unassigned slide");
}
const unlinked = assignSlideColor(assigned, "/a.jpg", null, "kem");
if (unlinked[0]?.colorId !== null) {
  fail("assignSlideColor(null) must unlink that color’s slide");
}

const a01Reel = productGalleryReel(a01);
const a01SecondColorId = a01.colors[1]?.id;
if (a01Reel.length !== 2 || a01Reel[0]?.colorId !== a01FirstColor || a01Reel[1]?.colorId !== a01SecondColorId) {
  fail("A01 reel is two unique tagged photos, one per color");
}
if (a01SecondColorId && firstReelIndexForColor(a01Reel, a01SecondColorId) !== 1) {
  fail("A01 second color must roll to its own photo, not a cloned cover");
}
if (new Set(a01Reel.map((slide) => slide.src)).size !== a01Reel.length) {
  fail("Reel must not clone the same JPEG");
}

const taggedReel = productGalleryReel({
  ...a01,
  colors: [
    { id: "kem", hex: "#F4F0E8", name: "Kem", note: "" },
    { id: "xanh", hex: "#1C2A4A", name: "Xanh", note: "" },
  ],
  images: [
    { src: "/products/A01/kem.jpg", colorId: "kem", order: 1 },
    { src: "/products/A01/cover.jpg", colorId: null, order: 2 },
    { src: "/products/A01/xanh.jpg", colorId: "xanh", order: 3 },
  ],
});
if (taggedReel.map((slide) => slide.colorId).join(",") !== "kem,xanh,") {
  fail("Tagged photos first (Kem, Xanh), then shared — unique srcs");
}
if (firstReelIndexForColor(taggedReel, "xanh") !== 1) {
  fail("Color pick must roll to that color’s first tagged slide");
}

const adminColors = readFileSync(path.join(process.cwd(), "components/admin-colors.tsx"), "utf8");
if (!adminColors.includes("moveLinkedSlide") || !adminColors.includes("admin-link-slide")) {
  fail("Admin color cards must link/reorder slides (image.colorId)");
}

console.log("media bind smoke ok");
