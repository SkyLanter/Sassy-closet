import { readFileSync } from "node:fs";
import path from "node:path";
import {
  assertAsiaSizesOnly,
  emptyFitCm,
  hidesEmptyAsiaLetterRow,
  inboxForFitLine,
  isAsiaSizeLetter,
  parseAsiaSizes,
  parseFitCm,
} from "../lib/asia-size";
import { statusNote } from "../lib/dropship-copy";
import { letterPickerOptions } from "../lib/catalog";
import { categoryAriaLabel } from "../lib/categories";
import { FEATURED_ALL_ARIA, lookCountLabel } from "../lib/look-count";
import { MA_LETTERS } from "../lib/ma";
import {
  COLOR_FIELD_LEGEND,
  SIZE_FIELD_LEGEND,
  EMPTY_GALLERY_MARK,
  ALL_PHOTOS_LABEL,
  SKIP_TO_LOOKS,
  SHOP_ERROR_BODY,
  copyMaDone,
  copyMaDoneAria,
  copyMaLabel,
  emptyGalleryAnnouncement,
  galleryReelLabel,
  messageAria,
  messageForRealPhotos,
  morePhotosLabel,
  photoIndexLabel,
  photoPositionLabel,
  viewingColorLine,
} from "../lib/pdp-copy";
import { validateItemDraft, type ItemDraft } from "../lib/item-draft";
import { coverSrcForColor, imagesForColor } from "../lib/product-media";
import { assertColorsReadyForSell, parseCatalogDocument } from "../lib/product-parse";
import { productJsonLd } from "../lib/seo";
import { toShopLook } from "../lib/shop-look";
import type { Product } from "../lib/types";

function fail(message: string): never {
  throw new Error(message);
}

function read(rel: string): string {
  return readFileSync(path.join(process.cwd(), rel), "utf8");
}

const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as unknown,
);

for (const product of seed.products) {
  if (product.sizes.length > 0) {
    fail(`Seed ${product.ma} invented Asia sizes`);
  }
  if (
    product.fitCm.bustChestCm !== null ||
    product.fitCm.waistCm !== null ||
    product.fitCm.lengthCm !== null
  ) {
    fail(`Seed ${product.ma} invented fit cm`);
  }
}

if (parseAsiaSizes(["S", "US M", "XXS", "2XL", "s"]).join(" ") !== "S 2XL") {
  fail("parseAsiaSizes must keep Asia letters only and drop US / XXS");
}
if (parseFitCm({ bustChestCm: 88, waistCm: "M", lengthCm: -1 }).bustChestCm !== 88) {
  fail("parseFitCm must keep stored cm only");
}
if (parseFitCm({ bustChestCm: 88, waistCm: "M", lengthCm: -1 }).waistCm !== null) {
  fail("parseFitCm must not invent cm from a letter");
}

try {
  assertAsiaSizesOnly(["US"]);
  fail("US size must be rejected");
} catch (error) {
  if (!(error instanceof Error) || !error.message.includes("Never US")) {
    fail("US size error must say Never US");
  }
}

if (!isAsiaSizeLetter("2XS") || isAsiaSizeLetter("XXS") || isAsiaSizeLetter("US")) {
  fail("Asia letters are 2XS–2XL only");
}

const twoTone: Product = {
  ...seed.products[0]!,
  colors: [
    { id: "cblackcolor01", hex: "#111111", name: "Black", note: "Hoa" },
    { id: "ccamelcolor01", hex: "#B08968", name: "Camel", note: "" },
  ],
  images: [
    { src: "/products/A01/cover.jpg", colorId: "cblackcolor01", order: 1 },
    { src: "/products/A01/shared.jpg", colorId: null, order: 2 },
    { src: "/products/A01/camel.jpg", colorId: "ccamelcolor01", order: 3 },
  ],
};

const blackView = imagesForColor(twoTone, "cblackcolor01").map((image) => image.src);
if (blackView.join(" ") !== "/products/A01/cover.jpg /products/A01/shared.jpg") {
  fail(`Black view must be tagged ∪ untagged, got ${blackView.join(" ")}`);
}
if (blackView.includes("/products/A01/camel.jpg")) {
  fail("Black view must not show another color’s photo");
}

const emptyMa: Product = {
  ...twoTone,
  images: [{ src: "/products/A01/camel.jpg", colorId: "ccamelcolor01", order: 1 }],
};
if (imagesForColor(emptyMa, "cblackcolor01").length !== 0) {
  fail("Empty color view must stay empty — never another mã or a CSS circle");
}
if (coverSrcForColor(emptyMa, "cblackcolor01") !== undefined) {
  fail("coverSrcForColor must not fall back to coverSrc when the color has no shots");
}

const a02 = seed.products.find((product) => product.ma === "A02");
if (!a02 || a02.colors.map((color) => color.id).join(",") !== "cham-bi") {
  fail("A02 must show Chấm bi — never A01 Kem/Xanh");
}
if (a02.colors.some((color) => color.hex === "#F4F0E8" || color.hex === "#1C2A4A")) {
  fail("A02 must not carry A01 hexes");
}
if (imagesForColor(a02, "kem").length !== 0 || coverSrcForColor(a02, "kem") !== undefined) {
  fail("A02 Kem is not stored on that row");
}

const chips = readFileSync(path.join(process.cwd(), "components", "color-name-chips.tsx"), "utf8");
if (chips.includes("bg-ink") || chips.includes("backgroundColor") || chips.includes("color.hex")) {
  fail("Customer chips are text + gold hairline, never ink pills or hex discs");
}
if (!chips.includes("h-px") || !chips.includes("bg-gold")) {
  fail("Selected chip must be a gold hairline");
}

assertColorsReadyForSell({
  ...twoTone,
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
});

const draft: ItemDraft = {
  titleEn: "Top",
  titleVn: "Áo",
  descriptionEn: "One unique top.",
  descriptionVn: "Áo.",
  status: "available",
  priceInput: "25",
  colors: [{ id: "cblackcolor01", hex: "#111111", name: "Black", note: "Hoa" }],
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
  sizes: ["S"],
  fitCm: { ...emptyFitCm(), bustChestCm: 88 },
  fulfillment: "dropship",
  sourceLink: "",
};
const draftError = validateItemDraft(draft);
if (draftError) {
  fail(`Named color without a tagged photo must Save, got ${draftError}`);
}

const nameless = validateItemDraft({
  ...draft,
  colors: [{ id: "cblackcolor01", hex: "#111111", name: "   ", note: "" }],
});
if (!nameless || !nameless.includes("name")) {
  fail("Nameless color must still fail");
}

const usDraft = validateItemDraft({
  ...draft,
  sizes: ["US" as unknown as (typeof draft.sizes)[number]],
});
if (!usDraft || !usDraft.includes("Never US")) {
  fail("Draft must reject a US size");
}

if (!hidesEmptyAsiaLetterRow("P") || !hidesEmptyAsiaLetterRow("H")) {
  fail("PK / hair / thermos hide an empty letter row");
}
if (hidesEmptyAsiaLetterRow("A") || hidesEmptyAsiaLetterRow("S")) {
  fail("Tops / sets must show Inbox for fit when empty");
}
if (inboxForFitLine("A01") !== "Inbox A01 for fit") {
  fail("Honest empty fit line");
}
const pdpPage = readFileSync(path.join(process.cwd(), "app/(shop)/m/[ma]/page.tsx"), "utf8");
if (pdpPage.includes("AsiaFit") || pdpPage.includes("inboxForFitLine")) {
  fail("Customer PDP must not show Inbox for fit");
}

const gallerySrc = read("components/product-gallery.tsx");
const sizeChips = read("components/size-name-chips.tsx");
if (!gallerySrc.includes("SizeNameChips") || !gallerySrc.includes('data-testid="pdp-size-chips"')) {
  fail("PDP must show catalog size chips under the photos when sizes exist");
}
if (!gallerySrc.includes("product.sizes.length > 0")) {
  fail("Size chips must hide when the catalog row has no letters");
}
if (gallerySrc.includes("ASIA_SIZE_LETTERS") || sizeChips.includes("ASIA_SIZE_LETTERS")) {
  fail("PDP must not paint the full 2XS–2XL row — only seller/catalog letters");
}
if (sizeChips.includes("useContentWave") || sizeChips.includes("Asia size") || sizeChips.includes("inboxForFitLine")) {
  fail("Size chips must stay catalog letters, no sheen, no Asia-size / Inbox for fit");
}
if (!sizeChips.includes("sizes.map") || !sizeChips.includes('data-testid="shop-size-chip"')) {
  fail("Size chips must map the look’s stored letters");
}

const h01Seed = seed.products.find((product) => product.ma === "H01");
if (!h01Seed) {
  fail("H01 missing");
}
if (toShopLook(h01Seed).sizes.length !== 0) {
  fail("Seed H01 must not invent size chips");
}
const a01Sized = toShopLook({ ...seed.products.find((product) => product.ma === "A01")!, sizes: ["L", "S", "US" as never, "M"] });
if (a01Sized.sizes.join(" ") !== "S M L") {
  fail("Shop look sizes must keep catalog Asia letters only, in 2XS–2XL order");
}
const honestEmpty = toShopLook({
  ...seed.products.find((product) => product.ma === "A01")!,
  sizes: ["均码", "L", "2xs", "XXL"] as never,
});
if (honestEmpty.sizes.join(" ") !== "2XS L") {
  fail("均码 and non-Asia tokens stay off the chip row; letters stay on the 2XS–2XL scale");
}
if (toShopLook({ ...seed.products.find((product) => product.ma === "H01")!, sizes: ["均码"] as never }).sizes.length !== 0) {
  fail("均码 alone must stay an honest empty chip row");
}

const hold = seed.products.find((product) => product.ma === "P02");
if (!hold) {
  fail("P02 missing");
}
const holdNote = statusNote(hold);
if (holdNote) {
  fail("Inbox-price PDP must not print a how-we-buy note");
}
if (/\bHold\b/.test(holdNote) || /Tạm giữ/.test(holdNote)) {
  fail("Customer PDP copy must not say Hold / Tạm giữ");
}

const available = statusNote(seed.products.find((product) => product.ma === "A01")!);
if (available) {
  fail("Priced PDP must not print Message-first / Taobao copy");
}
if (/\bHold\b/.test(available) || /\bAvailable\b/.test(available)) {
  fail("Priced dropship copy must not say Hold / Available");
}

const sized = { ...seed.products[0]!, sizes: ["M"] as Product["sizes"] };
const ld = productJsonLd(toShopLook(sized));
if (ld.size) {
  fail("Shopper JSON-LD must not list sizes — customer payload is name, price, description, colors, Message");
}
if (String(ld.size ?? "").includes("US")) {
  fail("JSON-LD size must never write US");
}

if (viewingColorLine("Black") !== "Đang xem: Black") {
  fail("Customer echo must be Đang xem: {name}");
}
if (COLOR_FIELD_LEGEND !== "Màu / Color" || EMPTY_GALLERY_MARK !== "—") {
  fail("Color legend / empty mark drifted");
}
if (SIZE_FIELD_LEGEND !== "Cỡ / Size" || /asia size/i.test(SIZE_FIELD_LEGEND)) {
  fail("Size legend must stay Cỡ / Size — never Asia size on the customer shop");
}
if (ALL_PHOTOS_LABEL !== "Tất cả ảnh · All photos") {
  fail("Unset gallery color label must stay bilingual");
}
if (
  emptyGalleryAnnouncement("Black") !==
  "Black. Không có ảnh màu này trên mã này · No photos for this color on this mã."
) {
  fail("Empty gallery stays on this mã");
}
if (messageForRealPhotos("A01") !== "Message A01") {
  fail("Empty hero must keep Message {MA}");
}
if (photoIndexLabel(1) !== "Xem ảnh 1 · Photo 1") {
  fail("Photo index labels must stay bilingual");
}
if (photoPositionLabel(1, 2) !== "Ảnh 1 / 2 · Photo 1 of 2") {
  fail("Gallery slide position must stay bilingual");
}
if (photoPositionLabel(1, 0) !== "") {
  fail("Empty galleries must not print Photo 1 of 0");
}
if (galleryReelLabel("A01") !== "Ảnh A01 · A01 photos") {
  fail("Gallery region aria must stay bilingual");
}
if (copyMaLabel("A01") !== "Sao chép A01 · Copy A01" || copyMaDone("A01") !== "Copied A01") {
  fail("Copy mã aria must stay bilingual; visible copied state stays English");
}
if (copyMaDoneAria("A01") !== "Đã sao chép A01 · Copied A01") {
  fail("Copied mã aria must stay bilingual");
}
if (messageAria("A01") !== "Nhắn tin A01 trên Messenger · Message A01 on Messenger") {
  fail("Message CTA aria must stay bilingual");
}
if (SKIP_TO_LOOKS !== "Tới looks · Skip to looks") {
  fail("Skip to looks must stay bilingual");
}
if (
  SHOP_ERROR_BODY !==
  "Nhắn tin trên Messenger, hoặc thử lại · Message on Messenger, or try again."
) {
  fail("Shop error body must stay bilingual");
}
if (categoryAriaLabel("A") !== "Áo · Tops" || FEATURED_ALL_ARIA !== "Tất cả · All") {
  fail("Category and All filter aria must stay bilingual from recorded names");
}
if (categoryAriaLabel("Q") !== "Quần · Bottoms") {
  fail("Q must stay Bottoms");
}
if (categoryAriaLabel("V") !== "Váy · Skirts") {
  fail("V must stay Skirts");
}
if (categoryAriaLabel("D") !== "Đầm · Dresses") {
  fail("D must stay Dresses");
}
if (categoryAriaLabel("K") !== "Áo khoác · Jackets") {
  fail("K must stay Jackets");
}
if (categoryAriaLabel("G") !== "Giày cao gót 35–41 · Shoes/High heels 35–41") {
  fail("G must stay Shoes/High heels 35–41");
}
if (categoryAriaLabel("B") !== "Túi · Bags") {
  fail("B must stay Bags");
}
if (categoryAriaLabel("P") !== "Phụ kiện · Accessories") {
  fail("P must stay Accessories");
}
if (categoryAriaLabel("H") !== "Phụ kiện tóc · Hair accessories") {
  fail("H must stay Hair accessories");
}
if (categoryAriaLabel("J") !== "Trang sức · Jewelry") {
  fail("J must stay Jewelry");
}
if (categoryAriaLabel("S") !== "Set đồ · Sets") {
  fail("S must stay Sets");
}
if (categoryAriaLabel("O") !== "Khác · Other") {
  fail("O must stay Other");
}
if (MA_LETTERS.join(",") !== "A,Q,V,D,K,G,B,P,H,J,S,O") {
  fail("Boss category letters must stay A Q V D K G B P H J S O");
}
if (letterPickerOptions().map((option) => option.letter).join(",") !== MA_LETTERS.join(",")) {
  fail("Admin letter picker must list every Boss letter in order");
}
if (letterPickerOptions()[0]?.label !== "A · Tops") {
  fail("Admin letter picker must stay A · Tops");
}
if (letterPickerOptions().find((option) => option.letter === "Q")?.label !== "Q · Bottoms") {
  fail("Admin letter picker must stay Q · Bottoms");
}
if (letterPickerOptions().find((option) => option.letter === "G")?.label !== "G · Shoes/High heels 35–41") {
  fail("Admin letter picker must stay G · Shoes/High heels 35–41");
}
if (letterPickerOptions().find((option) => option.letter === "H")?.label !== "H · Hair accessories") {
  fail("Admin letter picker must stay H · Hair accessories");
}
const productsLib = readFileSync(path.join(process.cwd(), "lib/products.ts"), "utf8");
if (!productsLib.includes("return [...MA_LETTERS]")) {
  fail("Nav/filters/tiles must list every Boss letter, including empty ones");
}
if (lookCountLabel(2, true) !== "2 looks nữa · 2 more looks") {
  fail("Related look count must stay bilingual like more photos");
}
if (morePhotosLabel(2) !== "Xem 2 ảnh nữa · 2 more photos") {
  fail("Overflow more-photos label must stay bilingual");
}

console.log("pdp color/size apply ok");
