import { readFileSync } from "node:fs";
import path from "node:path";
import {
  decodeShopSearchHeader,
  encodeShopSearchHeader,
  exactMaLook,
  filterLooksByQuery,
  firstSearchQueryParam,
  lookSearchHref,
  resolveLookSearch,
  suggestLooks,
  toLookSearchItems,
} from "../lib/look-search";
import { parseCatalogDocument } from "../lib/product-parse";
import { shopVisibleLooks } from "../lib/site-settings";

function fail(message: string): never {
  throw new Error(message);
}

function read(rel: string): string {
  return readFileSync(path.join(process.cwd(), rel), "utf8");
}

const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as unknown,
);
const looks = toLookSearchItems(shopVisibleLooks(seed.products));
const mas = new Set(looks.map((look) => look.ma));

if (!mas.has("A01") || !mas.has("H01")) {
  fail("Search index must keep seed A01 and H01");
}
if (mas.has("Z99") || mas.has("AO001")) {
  fail("Search must not invent Z99 or AO001");
}

const h01 = resolveLookSearch(looks, "h01");
if (h01.kind !== "exact" || h01.ma !== "H01" || lookSearchHref(h01) !== "/m/H01") {
  fail("Exact mã H01 must navigate to /m/H01");
}

const a01 = exactMaLook(looks, "A01");
if (!a01 || a01.ma !== "A01") {
  fail("A01 must resolve as an existing look");
}

const invented = resolveLookSearch(looks, "Z99");
if (invented.kind !== "results" || lookSearchHref(invented).startsWith("/m/")) {
  fail("Unknown mã must not navigate to a PDP");
}

const official = resolveLookSearch(looks, "AO001");
if (official.kind !== "results" || lookSearchHref(official).includes("/m/AO001")) {
  fail("Official AO001 must not become a shop PDP href");
}

const puppy = filterLooksByQuery(looks, "puppy");
if (!puppy.some((look) => look.ma === "A01")) {
  fail("Name search must find A01 Puppy cardigan");
}
if (puppy.some((look) => !mas.has(look.ma))) {
  fail("Name search must not invent mãs");
}

const rabbit = suggestLooks(looks, "rabbit");
if (!rabbit.some((look) => look.ma === "H01")) {
  fail("Name search must find H01 Rabbit hair bows");
}

const empty = resolveLookSearch(looks, "   ");
if (empty.kind !== "results" || lookSearchHref(empty) !== "/#featured-collection") {
  fail("Empty search must return to Looks");
}

if (firstSearchQueryParam(["H01", "A01"]) !== "H01" || firstSearchQueryParam(undefined) !== "") {
  fail("Search query param helper must keep the first value");
}

if (decodeShopSearchHeader(encodeShopSearchHeader("  puppy cardigan  ")) !== "puppy cardigan") {
  fail("Search header must round-trip a trimmed query");
}
if (decodeShopSearchHeader("%") !== "" || decodeShopSearchHeader(null) !== "") {
  fail("Broken search header must stay empty");
}

const header = read("components/header.tsx");
const featured = read("components/featured-board.tsx");
const layout = read("app/(shop)/layout.tsx");
const searchUi = read("components/header-search.tsx");
const pdp = read("app/(shop)/m/[ma]/page.tsx");

if (!header.includes("<HeaderSearch") || !header.includes("<MessengerCta")) {
  fail("Header search must sit next to Messenger on every shop page");
}
if (!header.includes("<HeaderSearchSheet") || !header.includes("<HeaderSearchProvider")) {
  fail("Search sheet must mount on the sticky header, not inside the field");
}
const navMark = header.indexOf("Danh mục · Categories");
const sheetMark = header.indexOf("<HeaderSearchSheet");
if (navMark < 0 || sheetMark < 0 || sheetMark < navMark) {
  fail("Opaque search sheet must sit after category tabs, not over them");
}
if (!layout.includes("ShopSearchProvider") || !pdp.includes("ProductLook")) {
  fail("PDP must keep shop layout search chrome");
}
if (featured.includes("shop-header-search") || featured.includes("HeaderSearch")) {
  fail("Home Looks must defer to header search");
}
if (!searchUi.includes('data-testid="shop-header-search"') || !searchUi.includes("/m/${look.ma}")) {
  fail("Header hits must be existing /m/{ma} links");
}
if (
  !searchUi.includes("shop-search-sheet") ||
  !searchUi.includes('data-testid="shop-search-sheet"') ||
  searchUi.includes("liquid-glass-sheet")
) {
  fail("Search empty panel must be opaque .shop-search-sheet, not liquid glass");
}
if (searchUi.includes('pathname === "/" ? searchParams.get("q") ?? "" : ""')) {
  fail("Leaving home must not wipe the header query");
}
if (!searchUi.includes("initialQuery") && !layout.includes("initialQuery")) {
  fail("Header search must paint the committed query on first load");
}
if (!layout.includes("decodeShopSearchHeader") || !layout.includes("relative sticky")) {
  fail("Shop chrome must carry the committed query and position the sheet below the tabs");
}
if (!featured.includes("searched.filter((product) => product.type === filter)")) {
  fail("Search must still honor the Looks tab");
}
if (searchUi.includes("/m/Z99") || searchUi.includes("AO001")) {
  fail("Header search must not hardcode invented mãs");
}

const categoryPage = read("app/(shop)/c/[slug]/page.tsx");
const catalog = read("components/looks-catalog.tsx");
if (!catalog.includes("filterLooksByQuery")) {
  fail("Category looks must follow the header query");
}
if (categoryPage.includes('type="search"') || catalog.includes('type="search"') || catalog.includes("Tìm mã")) {
  fail("Category pages must not host a second search box; header is the source of truth");
}

console.log("look search ok", {
  indexed: looks.length,
  exactH01: lookSearchHref(h01),
  puppy: puppy.map((look) => look.ma).join(","),
});
