import { readFileSync } from "node:fs";
import path from "node:path";
import robots from "../app/robots";
import { parseCatalogDocument } from "../lib/product-parse";
import { PUBLIC_FORBIDDEN_PHRASES, customerStockVoiceHit } from "../lib/public-safety";
import {
  categorySeo,
  organizationJsonLd,
  productJsonLd,
  productSeo,
  rootSeo,
  shopRobots,
} from "../lib/seo";
import { SITE } from "../lib/site";
import { parseSiteSettings } from "../lib/site-settings";
import { canonicalCategoryPath, canonicalMaPath } from "../lib/ma-url";
import { productShareCardCopy } from "../lib/share-card";
import {
  ANNOUNCE_A0,
  ANNOUNCEMENT_CHAR_BUDGET,
  ANNOUNCEMENT_LINES,
  categoryShareDescription,
  DROPSHIP_SPINE,
  HOME_DESCRIPTION,
  HOME_OG_TITLE,
  HOME_TITLE,
  HOW_TO_BUY_LINE,
  HOW_TO_BUY_DESCRIPTION,
  howToBuySteps,
  MEETUP_SHIP_DESCRIPTION,
  productShareDescription,
} from "../lib/trust-copy";

function fail(message: string): never {
  throw new Error(message);
}

const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as unknown,
);

if (shopRobots() && typeof shopRobots() === "object" && "index" in (shopRobots() as object)) {
  const robotsMeta = shopRobots() as { index?: boolean; follow?: boolean };
  if (robotsMeta.index !== false || robotsMeta.follow !== false) {
    fail("Test shop must stay noindex, nofollow until Boss flips official");
  }
}

const root = rootSeo();
if (root.robots && typeof root.robots === "object" && "index" in root.robots) {
  if (root.robots.index !== false) {
    fail("rootSeo must keep test noindex");
  }
}
if (
  !root.appleWebApp ||
  typeof root.appleWebApp !== "object" ||
  root.appleWebApp.statusBarStyle !== "black-translucent" ||
  root.appleWebApp.title !== SITE.name
) {
  fail("iOS status bar must stay black-translucent over the ink ticker");
}
if (
  root.appleWebApp &&
  typeof root.appleWebApp === "object" &&
  "capable" in root.appleWebApp &&
  root.appleWebApp.capable === true
) {
  fail("appleWebApp.capable must stay unset — do not install as a web app");
}
if (root.other?.["format-detection"] !== "telephone=no, date=no, address=no, email=no") {
  fail("iOS must not linkify prices as phone numbers");
}

const a01 = seed.products.find((product) => product.ma === "A01");
const a02 = seed.products.find((product) => product.ma === "A02");
const p02 = seed.products.find((product) => product.ma === "P02");
const p05 = seed.products.find((product) => product.ma === "P05");
if (!a01 || !a02 || !p02 || !p05) {
  fail("Hub mãs missing from seed");
}

const a01Desc = productShareDescription(a01);
const a02Desc = productShareDescription(a02);
const p02Desc = productShareDescription(p02);
if (a01Desc === a02Desc) {
  fail("A01 and A02 share descriptions must be unique");
}
if (a01Desc === HOME_DESCRIPTION || categoryShareDescription("A") === HOME_DESCRIPTION) {
  fail("Home meta must stay unique vs category and PDP");
}
if (!a01Desc.includes("A01") || !/puppy/i.test(a01Desc) || /Taobao/i.test(a01Desc)) {
  fail("A01 share/meta must name the mã and the garment — never Taobao");
}
if (/\bon hand\b/i.test(a01Desc) || /đang có/i.test(a01Desc)) {
  fail("A01 share/meta still pretends warehouse stock");
}
if (/\$23/.test(p02Desc) || /\$23/.test(productShareDescription(p05))) {
  fail("Inbox-price share copy must not invent $23");
}
if (/photo-check/i.test(p02Desc) || /not reserved/i.test(p02Desc) || /Taobao/i.test(p02Desc)) {
  fail("Inbox-price share copy must stay a clothes description");
}
if (/\bHold\b/.test(p02Desc) || /\bHold\b/.test(productShareDescription(p05))) {
  fail("Customer share copy must not say Hold");
}
const p02Card = productShareCardCopy(p02, "P02");
const p05Card = productShareCardCopy(p05, "P05");
if (/\bHold\b/.test(p02Card.subtitle) || /\bHold\b/.test(p05Card.subtitle)) {
  fail("Share-card OG must not print Hold");
}
if (!/inbox for price/i.test(p02Card.subtitle) || !/inbox for price/i.test(p05Card.subtitle)) {
  fail("Inbox-price share cards must stay Inbox for price");
}
if (p02.status !== "hold" || p02.priceUsd !== null || p05.status !== "hold" || p05.priceUsd !== null) {
  fail("P02 and P05 must stay Hold with no USD");
}
if (customerStockVoiceHit(p02Desc) || customerStockVoiceHit(productShareDescription(p05))) {
  fail("Share copy must not say Hold / Available / on hand");
}

for (const product of seed.products) {
  const text = `${productShareDescription(product)} ${product.descriptionEn} ${product.descriptionVn}`;
  if (/\bon hand\b/i.test(text) || /đang có/i.test(text)) {
    fail(`${product.ma} still pretends warehouse on-hand`);
  }
  if (/shippingRate|shippingDetails|flat \$\d/i.test(text)) {
    fail(`${product.ma} invented a ship $`);
  }
}

const a01Seo = productSeo(a01);
if (a01Seo.title !== "A01 · Puppy cardigan") {
  fail(`A01 title must stay A01 · Puppy cardigan, got ${String(a01Seo.title)}`);
}
if (a01Seo.description !== a01Desc) {
  fail("productSeo description must be the per-mã share string");
}
const a01Ld = productJsonLd(a01);
if (JSON.stringify(a01Ld.brand) !== JSON.stringify({ "@type": "Brand", name: SITE.name })) {
  fail("Product JSON-LD must name Sassy Closet as the brand");
}
if (a01Ld.inLanguage !== "en") {
  fail("Product JSON-LD must stay English");
}

const tops = categorySeo("A");
if (tops.description === HOME_DESCRIPTION || tops.description === a01Desc) {
  fail("Category meta must be unique vs home and PDP");
}

if (canonicalMaPath("/m/a01") !== "/m/A01") {
  fail("canonicalMaPath must map /m/a01 → /m/A01");
}
if (canonicalMaPath("/m/A01") !== null) {
  fail("canonical A01 must not redirect");
}
if (canonicalMaPath("/m/a01/opengraph-image") !== "/m/A01/opengraph-image") {
  fail("OG path must canonicalize the mã");
}
if (canonicalMaPath("/share/m/a01") !== "/share/m/A01") {
  fail("Share-card path must canonicalize the mã");
}
if (canonicalCategoryPath("/c/Ao") !== "/c/ao") {
  fail("Category slug must lowercase");
}
if (canonicalCategoryPath("/c/phu-kien-toc") !== "/c/toc") {
  fail("Stale Hair path /c/phu-kien-toc must 308 to /c/toc");
}
if (canonicalCategoryPath("/share/c/phu-kien-toc") !== "/share/c/toc") {
  fail("Share Hair path must follow the /c/toc slug");
}
if (canonicalCategoryPath("/c/toc") !== null) {
  fail("Canonical /c/toc must not redirect");
}

const rules = robots();
const rule = Array.isArray(rules.rules) ? rules.rules[0] : rules.rules;
if (!rule || rule.disallow === "/") {
  fail("Test robots.txt must not Disallow / — HTML noindex is the hide");
}
if (!JSON.stringify(rule.disallow).includes("/admin/") || !JSON.stringify(rule.disallow).includes("/api/")) {
  fail("robots.txt must keep /admin/ and /api/ out");
}

const org = organizationJsonLd(SITE.facebookPageUrl);
if (org["@type"] !== "Organization") {
  fail("Home must emit Organization JSON-LD");
}
if (JSON.stringify(org).includes("Thang")) {
  fail("Organization JSON-LD leaked a personal name");
}
if (org.logo && !String(org.logo).includes("/opengraph-image")) {
  fail("Organization JSON-LD logo must stay the lookbook share card");
}

const holdLd = productJsonLd(p02);
if (JSON.stringify(holdLd).includes("shippingRate") || JSON.stringify(holdLd).includes("shippingDetails")) {
  fail("Product JSON-LD must not invent shippingRate");
}
if ((holdLd.offers as { price?: string }).price) {
  fail("Hold JSON-LD must not invent USD");
}

const steps = howToBuySteps("A01");
if (steps.some((step) => /Taobao/i.test(step.en) || /Zelle/.test(step.en))) {
  fail("How-to-buy copy must not teach Taobao / Zelle on the customer shop");
}
if (steps.some((step) => /\bHold\b/.test(step.stage) || /\bHold\b/.test(step.en) || /\bHold\b/.test(step.vn))) {
  fail("How-to-buy must not say Hold to customers");
}
if (/Taobao/i.test(HOW_TO_BUY_DESCRIPTION) || /Zelle/.test(HOW_TO_BUY_DESCRIPTION)) {
  fail("How-to-buy meta must not print how we buy");
}
if (/\bHold\b/.test(HOW_TO_BUY_DESCRIPTION) || /\bHold\b/.test(DROPSHIP_SPINE)) {
  fail("How-to-buy spine must not say Hold");
}
if (/\$\d/.test(HOW_TO_BUY_LINE)) {
  fail("Lookbook how-to line must not invent a $");
}
if (/%\s|duty\s+\d/i.test(MEETUP_SHIP_DESCRIPTION)) {
  fail("Meetup & ship meta must never invent a duty %");
}

if (ANNOUNCEMENT_LINES.length !== 1 || ANNOUNCEMENT_LINES[0] !== ANNOUNCE_A0) {
  fail("Announcement must be the shop name only");
}
if (/unique|curated|A small closet/i.test(HOME_TITLE + HOME_DESCRIPTION + HOME_OG_TITLE)) {
  fail("Home meta must not invent unique/curated filler");
}
for (const line of ANNOUNCEMENT_LINES) {
  if (/\$\d/.test(line) || /flat \$/i.test(line)) {
    fail(`Announcement invented a $: ${line}`);
  }
  if (line.length > ANNOUNCEMENT_CHAR_BUDGET) {
    fail(`Announcement line exceeds h-8 budget (${line.length}>${ANNOUNCEMENT_CHAR_BUDGET}): ${line}`);
  }
  if (/how to buy|order Taobao|spot vs pre-sale/i.test(line)) {
    fail(`Announcement must not carry a how-to paragraph: ${line}`);
  }
}
const upgraded = parseSiteSettings({
  announcementLines: [
    "Facebook livestream",
    "Meetup or US-quote ship",
    "Message · Zelle after confirm",
  ],
  facebookPageUrl: SITE.facebookPageUrl,
});
if (upgraded.announcementLines.join("|") !== ANNOUNCE_A0) {
  fail("Legacy announcement must upgrade to the shop name only");
}
const livestreamOnly = parseSiteSettings({
  announcementLines: ["Facebook livestream"],
  facebookPageUrl: SITE.facebookPageUrl,
});
if (livestreamOnly.announcementLines[0] !== ANNOUNCE_A0) {
  fail("A lone Facebook livestream bar must upgrade to Sassy Closet");
}

const publicFiles = [
  "lib/trust-copy.ts",
  "lib/seo.ts",
  "lib/dropship-copy.ts",
  "lib/site.ts",
  "components/footer.tsx",
  "components/how-to-buy.tsx",
  "components/fulfill-line.tsx",
  "components/dropship-rail.tsx",
  "components/trust-ribbon.tsx",
  "app/(shop)/how-to-buy/page.tsx",
  "app/(shop)/meetup-ship/page.tsx",
];
for (const rel of publicFiles) {
  const text = readFileSync(path.join(process.cwd(), rel), "utf8");
  for (const phrase of PUBLIC_FORBIDDEN_PHRASES) {
    if (text.includes(phrase)) {
      fail(`${rel} leaks ${phrase}`);
    }
  }
  if (/Thang Tien Huynh/i.test(text)) {
    fail(`${rel} leaked the locked name`);
  }
  if (/e\.tb\.cn|source_link|Venmo|2[–-]4\s*(week|tuần)|duty-free|\$6\.95|flat \$\d/i.test(text)) {
    fail(`${rel} leaked staff ops or an invented ship/duty figure`);
  }
}

if (seed.settings.announcementLines.join("|") !== ANNOUNCEMENT_LINES.join("|")) {
  fail("Seed announcement must be the shop name only");
}

const shopSurfaces = [
  "app/(shop)/m/[ma]/page.tsx",
  "app/(shop)/(browse)/page.tsx",
  "components/product-card.tsx",
  "components/buy-bar.tsx",
  "components/footer.tsx",
  "components/product-price.tsx",
  "components/announcement-bar.tsx",
  "app/opengraph-image.tsx",
  "lib/og-card.tsx",
  "components/featured-board.tsx",
];
for (const rel of shopSurfaces) {
  const text = readFileSync(path.join(process.cwd(), rel), "utf8");
  if (/Taobao|\bZelle\b|photo-check|no cart|flat rate|Message-first/i.test(text)) {
    fail(`${rel} still prints how-we-buy language`);
  }
  if (/Unique pieces|curated closet|A small closet|Featured collection/i.test(text)) {
    fail(`${rel} still prints invented marketing filler`);
  }
}

console.log("seo + trust copy ok");
