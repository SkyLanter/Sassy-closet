import { readFileSync } from "node:fs";
import path from "node:path";
import { nextMaForLetter } from "../lib/ma";
import {
  cardBuyHint,
  HOLD_ASK_LABEL,
  listedLookDescriptionEn,
  listedLookDescriptionVn,
  SPOT_PRESALE_LINE,
  statusNote,
} from "../lib/dropship-copy";
import { DROPSHIP_RAIL } from "../lib/trust-copy";
import { customerOpsVoiceHit } from "../lib/public-safety";
import { WAREHOUSE_DANG_CO_ERROR, WAREHOUSE_ON_HAND_ERROR, warehouseVoiceError } from "../lib/warehouse-voice";
import { isMessengerAppDevice, messengerAppHref, messengerHref, messengerPageId, messengerTapHref } from "../lib/messenger";
import { HUB_SOURCE_LINKS, recordedHubSourceLink } from "../lib/hub-source-links";
import { parseCatalogDocument, toCatalogDocumentJson } from "../lib/product-parse";
import { shopSafeProduct } from "../lib/sell-contract";
import { shopLookPayloadLeak, toShopLook } from "../lib/shop-look";
import { shopVisibleLooks, shopVisibleProducts } from "../lib/site-settings";
import { absoluteMedia, categoryJsonLd, productJsonLd, productSeo } from "../lib/seo";
import { composeShipDraftMessage } from "../lib/ship-draft";
import { overlayCustomerStockVoice } from "../lib/catalog-store";
import { parseSourceLink } from "../lib/source-link";

function fail(message: string): never {
  throw new Error(message);
}

const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as unknown,
);
toCatalogDocumentJson(seed);

for (const product of seed.products) {
  if (product.fulfillment !== "dropship") {
    fail(`Seed ${product.ma} must default to dropship`);
  }
  // Seed links are real researched Taobao links — validate shape, never invent.
  try {
    parseSourceLink(product.sourceLink, product.ma);
  } catch (error) {
    fail(error instanceof Error ? error.message : `Seed ${product.ma} has a bad sourceLink`);
  }
  const copy = `${product.descriptionEn} ${product.descriptionVn}`;
  if (customerOpsVoiceHit(copy)) {
    fail(`Seed ${product.ma} still surfaces customer ops copy (${customerOpsVoiceHit(copy)})`);
  }
  if (/2[–-]4\s*(week|tuần)|\$6\.95|flat \$\d/i.test(copy)) {
    fail(`Seed ${product.ma} invented a ship $ or lead-time guarantee`);
  }
  switch (product.status) {
    case "available":
    case "hold":
      if (!product.descriptionEn.trim() || !product.descriptionVn.trim()) {
        fail(`Seed ${product.ma} needs a clothes description`);
      }
      break;
    case "sold":
      break;
    default: {
      const _exhaustive: never = product.status;
      fail(`Unhandled seed status ${_exhaustive}`);
    }
  }
}

for (const product of seed.products) {
  const leak = shopLookPayloadLeak(toShopLook(product));
  if (leak) {
    fail(`Shop look for ${product.ma} leaked ${leak}`);
  }
}
if (JSON.stringify(shopVisibleLooks(seed.products)).includes('"status"')) {
  fail("Shopper looks must omit status so RSC HTML cannot print Hold/Available");
}

const photoLessA03 = {
  ...seed.products[0],
  ma: "A03",
  type: "A" as const,
  images: [],
};
// A photo-less available mã still lists — with an honest empty gallery,
// never invented photos (the storefront announces the empty state).
const photoLessLook = shopVisibleLooks([photoLessA03]).find((look) => look.ma === "A03");
if (!photoLessLook) {
  fail("A photo-less available mã still lists as a look");
}
if (photoLessLook.images.length !== 0) {
  fail("Photo-less look must carry an empty gallery — never invented photos");
}
if (!shopVisibleProducts([photoLessA03]).some((product) => product.ma === "A03")) {
  fail("Admin catalog may still keep a photo-less extra");
}
// Every shop look traces back to a seed mã — never invent one.
const seedMas = new Set(seed.products.map((product) => product.ma));
for (const look of shopVisibleLooks(seed.products)) {
  if (!seedMas.has(look.ma)) {
    fail(`Do not invent ${look.ma} as a shop look`);
  }
}

if (warehouseVoiceError("One unique top on hand.", "Áo.", "dropship") !== WAREHOUSE_ON_HAND_ERROR) {
  fail("Dropship Save must reject “on hand”");
}
if (warehouseVoiceError("Listed look.", "Áo độc bản — một chiếc đang có.", "dropship") !== WAREHOUSE_DANG_CO_ERROR) {
  fail("Dropship Save must reject “đang có”");
}
if (warehouseVoiceError("Received locally.", "Hàng sẵn.", "on_hand") !== null) {
  fail("On-hand fulfillment may describe a received piece");
}

const dirtyHold = overlayCustomerStockVoice({
  ...seed,
  products: seed.products.map((product) =>
    product.ma === "P02"
      ? { ...product, descriptionEn: "Thermos on Hold (photo-check).", descriptionVn: "Bình đang Hold." }
      : product,
  ),
});
const cleanedP02 = dirtyHold.products.find((product) => product.ma === "P02");
if (!cleanedP02 || customerOpsVoiceHit(`${cleanedP02.descriptionEn} ${cleanedP02.descriptionVn}`)) {
  fail("Stale Blob ops copy on P02 must overlay garment seed copy");
}
if (cleanedP02.status !== "available" || cleanedP02.priceUsd !== 28) {
  fail("Copy overlay must not touch P02 status/price internally");
}

const seedA01 = seed.products.find((product) => product.ma === "A01");
const staffRewroteA01 = overlayCustomerStockVoice({
  ...seed,
  products: seed.products.map((product) =>
    product.ma === "A01"
      ? { ...product, titleEn: "Staff title", descriptionEn: "Nice admin rewrite." }
      : product,
  ),
});
const cleanedA01 = staffRewroteA01.products.find((product) => product.ma === "A01");
if (!seedA01 || !cleanedA01 || cleanedA01.titleEn !== seedA01.titleEn) {
  fail("Hub overlay must restore seed boutique titles");
}
if (cleanedA01.descriptionEn !== seedA01.descriptionEn) {
  fail("Hub overlay must restore seed garment copy, not a staff rewrite");
}

if (!seedA01) {
  fail("A01 missing for extra overlay");
}
// The extra-ops fixture must be a mã the seed does not have yet.
const extraOpsMa = nextMaForLetter("A", seed.products.map((product) => product.ma));
const extraOps = overlayCustomerStockVoice({
  ...seed,
  products: [
    ...seed.products,
    {
      ...seedA01,
      ma: extraOpsMa,
      titleEn: "Top",
      titleVn: "Áo",
      descriptionEn: `One unique top. Message ${extraOpsMa} to order — sourced after you inbox.`,
      descriptionVn: `Áo độc bản. Nhắn tin ${extraOpsMa} để đặt.`,
    },
  ],
});
const cleanedExtra = extraOps.products.find((product) => product.ma === extraOpsMa);
if (!cleanedExtra || cleanedExtra.descriptionEn !== "" || cleanedExtra.descriptionVn !== "") {
  fail("Extra mãs with invented unique/ops copy must overlay to a blank description");
}
if (/unique|listed |độc bản|sourced after/i.test(`${cleanedExtra.descriptionEn} ${cleanedExtra.descriptionVn}`)) {
  fail("Blanked extra copy must not keep filler words");
}
if (listedLookDescriptionEn(extraOpsMa) !== "" || listedLookDescriptionVn(extraOpsMa) !== "") {
  fail("Do not invent listed-look filler for extras");
}

const kept = parseSourceLink("https://e.tb.cn/h.example123", "A01");
if (kept !== "https://e.tb.cn/h.example123") {
  fail("Must keep a real e.tb.cn link");
}

try {
  parseSourceLink("https://www.amazon.com/foo", "A01");
  fail("Amazon link must be rejected");
} catch (error) {
  if (!(error instanceof Error) || !error.message.includes("Taobao")) {
    fail("Wrong error for invented non-Taobao link");
  }
}

try {
  parseSourceLink("https://made-up.shop/A01", "A01");
  fail("Invented shop link must be rejected");
} catch {
  // expected
}

if (parseSourceLink("", "A01") !== null || parseSourceLink(undefined, "A01") !== null) {
  fail("Missing sourceLink must stay null — do not invent");
}

for (const [ma, url] of Object.entries(HUB_SOURCE_LINKS)) {
  if (recordedHubSourceLink(ma) !== parseSourceLink(url, ma)) {
    fail(`Recorded hub link for ${ma} must parse as a Taobao URL`);
  }
}
if (recordedHubSourceLink("A03") !== null) {
  fail("A03 must not get a recorded hub link");
}

const staffA01 = { ...seed.products[0]!, sourceLink: recordedHubSourceLink("A01") };
if (!staffA01.sourceLink || shopSafeProduct(staffA01).sourceLink !== null) {
  fail("Customer product must hide the recorded staff link");
}
if (shopVisibleProducts([staffA01])[0]?.sourceLink !== null) {
  fail("Shop visible products must omit sourceLink");
}

const draft = composeShipDraftMessage("A01", "hold", {
  name: "Kelly",
  address: "123 Paper St",
  city: "SF",
  note: HOLD_ASK_LABEL,
});
if (!draft.includes("Mã A01") || !draft.includes(HOLD_ASK_LABEL)) {
  fail("Ship draft must include mã and Hold ask");
}
if (/\$\d/.test(draft) || /flat \$/i.test(draft)) {
  fail("Ship draft invented a ship $");
}

const availableDraft = composeShipDraftMessage("S01", "available", {
  name: "",
  address: "",
  city: "",
  note: "",
});
if (!availableDraft.includes("Mã S01") || /\$\d/.test(availableDraft)) {
  fail("Empty address draft must still carry mã and no $");
}

const href = messengerHref("https://www.facebook.com/profile.php?id=61594312648057");
if (href !== "https://m.me/61594312648057") {
  fail(`Messenger must open a plain Page chat, got ${href}`);
}
if (href.includes("text=") || href.includes("ref=") || href.includes("Hi%20Sassy") || href.includes("I%20would")) {
  fail(`Messenger must not prefill composed text, got ${href}`);
}
if (messengerHref("https://m.me/61594312648057?text=Hi%20Sassy") !== "https://m.me/61594312648057") {
  fail("Dirty m.me ?text= must strip to a plain Page chat");
}
if (messengerHref("")) {
  fail("Empty Page URL must not invent a Messenger target");
}
if (messengerAppHref("")) {
  fail("Empty Page URL must not invent a Messenger app target");
}
if (messengerAppHref("https://www.facebook.com/profile.php?id=61594312648057") !== "fb-messenger://user-thread/61594312648057") {
  fail("Phone Message must open the Page thread in the Messenger app");
}
if (messengerTapHref("https://www.facebook.com/profile.php?id=61594312648057", false) !== "https://m.me/61594312648057") {
  fail("Desktop Message must stay https://m.me/{pageId}");
}
if (messengerTapHref("https://www.facebook.com/profile.php?id=61594312648057", true) !== "fb-messenger://user-thread/61594312648057") {
  fail("Phone Message tap must use the Messenger app scheme");
}
if (!isMessengerAppDevice("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)") || !isMessengerAppDevice("Mozilla/5.0 (Linux; Android 14)")) {
  fail("iPhone and Android must use the Messenger app scheme");
}
if (isMessengerAppDevice("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")) {
  fail("Desktop Safari must stay on https://m.me");
}
if (messengerHref("https://www.facebook.com/profile.php?id=61594312648057").includes("facebook.com")) {
  fail("Message must never emit a Facebook profile URL");
}
if (messengerHref("https://example.com/nope") !== "https://m.me/61594312648057") {
  fail("Unparseable Page URL must still open the recorded m.me inbox");
}
if (messengerPageId("https://www.facebook.com/profile.php?id=61594312648057") !== "61594312648057") {
  fail("Page id must stay 61594312648057");
}
if (
  messengerHref("https://www.facebook.com/profile.php?id=61594312648057").includes("messenger.com") ||
  messengerHref("https://www.facebook.com/profile.php?id=61594312648057").includes("facebook.com/messages")
) {
  fail("Message must not open messenger.com or facebook.com/messages web");
}

const page = "https://www.facebook.com/profile.php?id=61594312648057";
const productHref = messengerHref(page);
if (productHref !== "https://m.me/61594312648057") {
  fail(`Message CTA must be a plain m.me chat, got ${productHref}`);
}
if (productHref.includes("profile.php") || productHref.includes("?")) {
  fail("Message CTA must not use a bare Facebook profile URL or query string");
}
const headerHref = messengerHref(page);
if (headerHref !== productHref || headerHref.includes("text=") || headerHref.includes("ref=")) {
  fail(`Header/footer Message must open the same empty m.me chat, got ${headerHref}`);
}
const holdHref = messengerHref(page);
if (holdHref.includes("text=") || /\$23/.test(holdHref) || holdHref.includes("P02")) {
  fail("Hold Message must not prefill P02 or invent $23");
}

const holdBase = seed.products.find((product) => product.ma === "P02");
if (!holdBase) {
  fail("P02 missing");
}
// Pin a Hold fixture — the seed's P02 is Available, so the hold checks below
// test JSON-LD behavior, not seed state.
const hold = { ...holdBase, status: "hold" as const, priceUsd: null };
const note = statusNote(hold);
if (note) {
  fail("Inbox-price PDP must not print a how-we-buy status note");
}
if (customerOpsVoiceHit(note ?? "ok") && note) {
  fail("Inbox-price PDP copy must not say Hold / Available / on hand");
}
const ld = productJsonLd(hold);
const offer = ld.offers as { price?: string; availability?: string };
if (offer.price) {
  fail("Hold JSON-LD must not invent USD");
}
if (offer.availability) {
  fail("Hold JSON-LD must not print availability / PreOrder / InStock");
}

const priced = seed.products.find((product) => product.ma === "A01");
if (!priced) {
  fail("A01 missing");
}
const pricedLd = productJsonLd(priced);
const pricedOffer = pricedLd.offers as { availability?: string; price?: string };
if (pricedOffer.availability === "https://schema.org/InStock") {
  fail("Dropship available must not pretend warehouse InStock");
}
if (pricedOffer.price !== "30.00") {
  fail("A01 JSON-LD must keep Boss $30");
}

if (cardBuyHint(hold) !== "Message to buy") {
  fail("Hold card hint helper stays Message to buy (not rendered on cards)");
}
if (cardBuyHint(priced) !== "Message to buy") {
  fail("Available card hint helper stays Message to buy");
}
if (/\$23/.test(statusNote(hold))) {
  fail("Hold PDP copy must never invent $23");
}

const p05Base = seed.products.find((product) => product.ma === "P05");
if (!p05Base) {
  fail("P05 missing");
}
// Pin Hold fixtures — the seed's P02/P05 are Available, so these checks
// test hold-product rendering, not seed state.
const p05 = { ...p05Base, status: "hold" as const, priceUsd: null };
if (hold.status !== "hold" || hold.priceUsd !== null || p05.status !== "hold" || p05.priceUsd !== null) {
  fail("P02 and P05 fixtures must stay Hold with no USD");
}

const availableNote = statusNote(priced);
if (availableNote) {
  fail("Priced PDP must not print a how-we-buy status note");
}
if (customerOpsVoiceHit(availableNote) && availableNote) {
  fail("Priced dropship note must not say Hold / Available / on hand");
}
if (!SPOT_PRESALE_LINE.includes("Spot / pre-sale") || !SPOT_PRESALE_LINE.includes("chốt khi inbox")) {
  fail("Spot / pre-sale strings may live in the copy bank, not on the PDP");
}
if (DROPSHIP_RAIL !== "Message on Messenger.") {
  fail("Unused rail copy must stay boutique Message on Messenger");
}
const railSrc = readFileSync(path.join(process.cwd(), "components/dropship-rail.tsx"), "utf8");
if (railSrc.includes("TB_ORDER_LINE") || /Taobao|Zelle|no cart/i.test(railSrc)) {
  fail("PDP rail must not print how-we-buy language");
}

const pdpPage = readFileSync(path.join(process.cwd(), "app/(shop)/m/[ma]/page.tsx"), "utf8");
const lookSrc = readFileSync(path.join(process.cwd(), "components/product-look.tsx"), "utf8");
const cardSrc = readFileSync(path.join(process.cwd(), "components/product-card.tsx"), "utf8");
const buyBar = readFileSync(path.join(process.cwd(), "components/buy-bar.tsx"), "utf8");
if (pdpPage.includes("ProductStatusBadge") || lookSrc.includes("ProductStatusBadge") || cardSrc.includes("ProductStatusBadge") || buyBar.includes("ProductStatusBadge")) {
  fail("Customer grid / PDP / buy bar must not render status badges");
}
if (
  pdpPage.includes("HowToBuy") ||
  pdpPage.includes("DropshipRail") ||
  pdpPage.includes("ShipDraftForm") ||
  pdpPage.includes("AsiaFit") ||
  pdpPage.includes("ProductStatusNote") ||
  lookSrc.includes("HowToBuy") ||
  lookSrc.includes("DropshipRail") ||
  lookSrc.includes("ShipDraftForm") ||
  lookSrc.includes("AsiaFit") ||
  lookSrc.includes("ProductStatusNote")
) {
  fail("Customer PDP must be name, price, description, colors, catalog sizes, Message");
}
const gallerySrc = readFileSync(path.join(process.cwd(), "components/product-gallery.tsx"), "utf8");
if (!lookSrc.includes("ProductPageTitle") || !lookSrc.includes("ProductPrice") || !lookSrc.includes("ProductDescription") || !gallerySrc.includes("ColorNameChips") || !gallerySrc.includes("SizeNameChips") || !lookSrc.includes("MessengerCta")) {
  fail("PDP must be name, price, description, colors and catalog sizes under photos, Message");
}
if (!cardSrc.includes("displayDescription") || cardSrc.includes("ProductBuyHint")) {
  fail("Cards must show garment copy when present, never Message-to-buy ops hints");
}
if (buyBar.includes("ShipDraftForm") || buyBar.includes("FulfillLine") || buyBar.includes("Address +")) {
  fail("Phone bar must be mã, price, Message only");
}
if (lookSrc.includes("product.status") || cardSrc.includes("product.status") || buyBar.includes("product.status")) {
  fail("Customer chrome must not read status into the shopper payload");
}

if (pdpPage.includes("SPOT_PRESALE_LINE") || pdpPage.includes("spot-presale")) {
  fail("PDP must not show spot / pre-sale stock microcopy");
}
if (pdpPage.includes("more piece") || pdpPage.includes("more pieces")) {
  fail("PDP related row must not use piece/stock count language");
}

const tops = seed.products.filter((product) => product.type === "A");
const list = categoryJsonLd("Tops", "ao", tops);
if (list["@type"] !== "ItemList") {
  fail("Category JSON-LD must be ItemList");
}
if (list.numberOfItems !== tops.length) {
  fail("ItemList count must match shop-visible tops");
}
const elements = list.itemListElement as Array<{ name?: string; url?: string }>;
if (!elements.some((item) => item.name?.includes("A01"))) {
  fail("ItemList must name A01");
}
if (elements.some((item) => item.url)) {
  fail("ItemList must not invent product URLs when shop origin is unset");
}

const prevOrigin = process.env.NEXT_PUBLIC_SHOP_URL;
process.env.NEXT_PUBLIC_SHOP_URL = "https://example.test";
const withOrigin = categoryJsonLd("Tops", "ao", tops);
const originElements = withOrigin.itemListElement as Array<{ url?: string }>;
if (withOrigin.url !== "https://example.test/c/ao") {
  fail("ItemList url must use the public shop origin when set");
}
if (originElements[0]?.url !== "https://example.test/m/A01") {
  fail("ItemList item url must be absolute only when origin is set");
}
const og = productSeo(priced);
const ogImage = og.openGraph?.images;
const ogUrl =
  Array.isArray(ogImage) && ogImage[0] && typeof ogImage[0] === "object" && "url" in ogImage[0]
    ? String(ogImage[0].url)
    : "";
if (ogUrl !== "https://example.test/share/m/A01") {
  fail(`Product OG image must be the 1200×630 share card when origin is set, got ${ogUrl}`);
}
if (absoluteMedia("/editorial/ao.jpg") !== "https://example.test/editorial/ao.jpg") {
  fail("absoluteMedia must prefix the public origin");
}
if (prevOrigin) {
  process.env.NEXT_PUBLIC_SHOP_URL = prevOrigin;
} else {
  delete process.env.NEXT_PUBLIC_SHOP_URL;
}

const ctaFiles = [
  "components/messenger-cta.tsx",
  "components/header.tsx",
  "components/footer.tsx",
  "components/buy-bar.tsx",
  "app/(shop)/m/[ma]/page.tsx",
];
for (const rel of ctaFiles) {
  const text = readFileSync(path.join(process.cwd(), rel), "utf8");
  if (/Shop now|Add to cart|Buy with card/i.test(text)) {
    fail(`${rel} added a cart / Shop now CTA`);
  }
  if (text.includes("openMessengerChat")) {
    fail(`${rel} must not hijack Messenger taps`);
  }
  if (rel === "components/messenger-cta.tsx" && (text.includes("setTimeout") || text.includes("preventDefault"))) {
    fail(`${rel} must not delay a web hop after a Messenger tap`);
  }
}

console.log("dropship + ship-draft ok");
