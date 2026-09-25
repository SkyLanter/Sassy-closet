import { createHash } from "node:crypto";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
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
import { coverSrcForColor, hasOwnShopPhotos, imagesForColor, srcBelongsToMa } from "../lib/product-media";
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
if (a01.colors.map((color) => color.id).join(",") !== "kem,xanh") {
  fail(`A01 colors must be kem,xanh got ${a01.colors.map((color) => color.id).join(",")}`);
}
if (a01.images.some((image) => image.src.includes(".svg"))) {
  fail("A01 must not use an SVG placeholder");
}
if (a01.images[0]?.src !== "/products/A01/cover.jpg" || a01.images[0]?.colorId !== "kem") {
  fail("A01 cover is the real lavender cardigan, tagged kem");
}
if (a01.images[1]?.src !== "/products/A01/photo-2.jpg" || a01.images[1]?.colorId !== "xanh") {
  fail("A01 photo-2 is the yellow puppy cardigan, tagged xanh");
}
if (a01.images[0]?.order !== 1 || a01.images[1]?.order !== 2) {
  fail("A01 photos must stay order 1 then 2");
}
const a01CoverPath = path.join(process.cwd(), "public", "products", "A01", "cover.jpg");
if (existsSync(path.join(process.cwd(), "public", "products", "A01", "cover.svg"))) {
  fail("Delete the AI cover.svg for A01");
}
if (!existsSync(a01CoverPath) || statSync(a01CoverPath).size < 300_000) {
  fail("A01 cover.jpg must be the real lavender JPEG, not the 205KB AI camisole");
}
const a01Jpeg = readFileSync(a01CoverPath);
if (a01Jpeg[0] !== 0xff || a01Jpeg[1] !== 0xd8) {
  fail("A01 cover must be a JPEG");
}

const remapped = applyRecordedHubColors({
  ...a01,
  colors: [
    { id: "ckemivory01", hex: "#F4F0E8", name: "Kem", note: "" },
    { id: "cxanhnavy01", hex: "#1C2A4A", name: "Xanh", note: "" },
  ],
  images: [{ src: "/products/A01/cover.jpg", colorId: "ckemivory01", order: 1 }],
});
if (remapped.colors.map((color) => color.id).join(",") !== "kem,xanh") {
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
    { src: "/products/A01/cover.jpg", colorId: "kem", order: 1 },
    { src: "/products/A01/cover.jpg", colorId: null, order: 2 },
  ],
});
if (!tagged.ok) {
  fail(tagged.error);
}
const savedA01 = tagged.products.find((product) => product.ma === "A01");
if (!savedA01 || savedA01.images[0]?.colorId !== "kem" || savedA01.images[1]?.colorId !== null) {
  fail("A01 must store kem or null — not an invented slug");
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
if (!k01 || k01.colors.length !== 0) {
  fail("K01 must have no recorded colors");
}
if (recordedHubSlugs("K01").length !== 0 || !hubColorLocked("K01")) {
  fail("K01 stays locked with empty recorded slugs");
}
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

function publicJpeg(ma: string, file: string): Buffer {
  const disk = path.join(process.cwd(), "public", "products", ma, file);
  if (!existsSync(disk)) {
    fail(`${ma} is missing ${file} — extra pack frame must be on disk`);
  }
  const buf = readFileSync(disk);
  if (buf[0] !== 0xff || buf[1] !== 0xd8) {
    fail(`${ma}/${file} must be a JPEG`);
  }
  if (buf.length < 80_000) {
    fail(`${ma}/${file} is too small to be a real intake photo`);
  }
  return buf;
}

const extraPackGalleries: { ma: string; files: string[]; colorIds: string }[] = [
  { ma: "P02", files: ["cover.jpg", "photo-2.jpg"], colorIds: "do," },
  { ma: "P03", files: ["cover.jpg", "photo-2.jpg", "photo-3.jpg"], colorIds: ",," },
  { ma: "P04", files: ["cover.jpg", "photo-2.jpg"], colorIds: "kem," },
  { ma: "P05", files: ["cover.jpg", "photo-2.jpg", "photo-3.jpg"], colorIds: "hong,hong,xanh" },
  { ma: "A02", files: ["cover.jpg", "photo-2.jpg"], colorIds: "ca0200,ca0200" },
  { ma: "H01", files: ["cover.jpg", "photo-2.jpg", "photo-3.jpg"], colorIds: ",," },
  { ma: "K01", files: ["cover.jpg"], colorIds: "" },
];

for (const row of extraPackGalleries) {
  const product = seed.products.find((item) => item.ma === row.ma);
  if (!product) {
    fail(`${row.ma} missing`);
  }
  const srcs = product.images.map((image) => image.src.split("?")[0] ?? "");
  const expected = row.files.map((file) => `/products/${row.ma}/${file}`);
  if (srcs.join(" ") !== expected.join(" ")) {
    fail(`${row.ma} gallery must be ${expected.join(" ")} after the first shot`);
  }
  if (product.images.map((image) => image.colorId).join(",") !== row.colorIds) {
    fail(`${row.ma} extra frames keep recorded binds — do not invent a new color`);
  }
  const hashes = row.files.map((file) => createHash("md5").update(publicJpeg(row.ma, file)).digest("hex"));
  if (new Set(hashes).size !== hashes.length) {
    fail(`${row.ma} must not clone the same JPEG as a fake peek`);
  }
  const reel = productGalleryReel(product);
  if (reel.length !== row.files.length) {
    fail(`${row.ma} reel is ${row.files.length} unique pack photos`);
  }
  const folder = path.join(process.cwd(), "public", "products", row.ma);
  const onDisk = readdirSync(folder).filter((name) => /\.jpe?g$/i.test(name));
  if (row.ma === "K01" && onDisk.includes("photo-2.jpg")) {
    fail("K01/002 is the same JPEG as 001 — do not add a cloned photo-2");
  }
  const diskHashes = onDisk.map((file) =>
    createHash("md5").update(readFileSync(path.join(folder, file))).digest("hex"),
  );
  if (new Set(diskHashes).size !== diskHashes.length) {
    fail(`${row.ma} public folder has two files with the same bytes`);
  }
}

const p05 = seed.products.find((product) => product.ma === "P05");
if (!p05 || p05.status !== "hold" || p05.priceUsd !== null) {
  fail("P05 stays Hold with no USD");
}
if (p05.colors.map((color) => color.id).join(",") !== "hong,do,xanh") {
  fail("P05 recorded slugs are hong,do,xanh");
}
if (p05.images.map((image) => image.colorId).join(",") !== "hong,hong,xanh") {
  fail("P05 binds My Melody + Piano to hồng, Kuromi to xanh — not a fake đỏ slide");
}
if (p05.images.some((image) => image.colorId === "do")) {
  fail("Do not invent a đỏ bind on P05");
}

const p02 = seed.products.find((product) => product.ma === "P02");
if (!p02 || p02.status !== "hold" || p02.priceUsd !== null) {
  fail("P02 stays Hold with no USD");
}

const a02 = seed.products.find((product) => product.ma === "A02");
if (!a02 || a02.colors[0]?.id !== "ca0200") {
  fail("A02 keeps ca0200 Off-white (seed) — do not invent colors");
}
if (a02.colors.some((color) => color.id === "ca0100" || color.id === "ca0101")) {
  fail("A02 must not borrow A01 colors");
}
if (!srcBelongsToMa("/products/A02/cover.jpg", "A02") || srcBelongsToMa("/products/A01/cover.jpg", "A02")) {
  fail("A02 folder filter must keep A02 files and drop A01");
}
if (!srcBelongsToMa("/products/A04/cover.jpg", "A03")) {
  fail("Rename extras may keep the previous folder so thumbs do not 404");
}
if (hasOwnShopPhotos({ ma: "A03", colors: [], images: [] })) {
  fail("A03 with no images has no shop photos");
}
if (!hasOwnShopPhotos(a01)) {
  fail("A01 must keep its own listing photos");
}
const remappedA02 = applyHubColorNames([
  {
    ...a02,
    colors: a01.colors,
    images: a01.images,
  },
])[0];
if (!remappedA02 || remappedA02.colors.some((color) => color.id === "kem" || color.id === "xanh")) {
  fail("Stale foreign colors on A02 must be remapped/dropped");
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

if (bindColorId(a01.colors, "xanh") !== "xanh" || bindColorId(a01.colors, "hong") !== null) {
  fail("bindColorId only accepts a slug already on that mã");
}

const kemView = imagesForColor(savedA01!, "kem");
if (kemView.length !== 2) {
  fail("Kem view is tagged ∪ untagged on this mã");
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
if (a01Reel.length !== 2 || a01Reel[0]?.colorId !== "kem" || a01Reel[1]?.colorId !== "xanh") {
  fail("A01 reel is two unique tagged photos (lavender kem, yellow xanh)");
}
if (firstReelIndexForColor(a01Reel, "xanh") !== 1) {
  fail("A01 Xanh must roll to photo-2, not a cloned cover");
}
if (new Set(a01Reel.map((slide) => slide.src)).size !== a01Reel.length) {
  fail("Reel must not clone the same JPEG");
}

const taggedReel = productGalleryReel({
  ...a01,
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
