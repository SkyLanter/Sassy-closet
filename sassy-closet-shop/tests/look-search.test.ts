import assert from "node:assert/strict";
import test from "node:test";
import {
  encodeShopSearchHeader,
  exactMaLook,
  filterLooksByQuery,
  foldSearchText,
  LOOK_SEARCH_PLACEHOLDER,
  lookSearchHref,
  looseMaCandidate,
  resolveLookSearch,
  searchSubmitQuery,
  suggestLooks,
  type LookSearchItem,
} from "../lib/look-search";

const BOOK: LookSearchItem[] = [
  { ma: "A15", titleEn: "Heather knit top", titleVn: "Áo len" },
  { ma: "A02", titleEn: "Knit top", titleVn: "Áo" },
  { ma: "D02", titleEn: "Silk dress", titleVn: "Đầm lụa" },
  { ma: "D04", titleEn: "Linen dress", titleVn: "Đầm" },
  { ma: "V03", titleEn: "Pleat skirt", titleVn: "Váy" },
  { ma: "Q01", titleEn: "Wide pants", titleVn: "Quần" },
  { ma: "P04", titleEn: "Clip", titleVn: "Kẹp hồng" },
  { ma: "S02", titleEn: "Two piece", titleVn: "Set đồ" },
];

const WITH_PADDED: LookSearchItem[] = [
  ...BOOK,
  { ma: "A015", titleEn: "Other top", titleVn: "Áo khác" },
];

function mas(query: string, looks: LookSearchItem[] = BOOK): string[] {
  return filterLooksByQuery(looks, query).map((look) => look.ma);
}

test("search folds accents and đ without changing copy", () => {
  assert.equal(LOOK_SEARCH_PLACEHOLDER, "Tìm mã (A15)… / Search mã");
  assert.equal(foldSearchText("  Áo   Đầm  "), "ao dam");
  assert.deepEqual(mas("ao"), mas("áo"));
  assert.deepEqual(mas("dam"), mas("đầm"));
  assert.deepEqual(mas("vay"), mas("váy"));
  assert.deepEqual(mas("quan"), mas("quần"));
  assert.deepEqual(mas("hong"), mas("hồng"));
});

test("search matches category words, plurals, and any token order", () => {
  assert.deepEqual(mas("ao"), ["A15", "A02"]);
  assert.deepEqual(mas("dam"), ["D02", "D04"]);
  assert.deepEqual(mas("vay"), ["V03"]);
  assert.deepEqual(mas("quan"), ["Q01"]);
  assert.deepEqual(mas("hong"), ["P04"]);
  assert.deepEqual(mas("phu kien"), ["P04"]);
  assert.deepEqual(mas("set"), ["S02"]);
  assert.deepEqual(mas("heather"), ["A15"]);
  assert.deepEqual(mas("tops"), ["A15", "A02"]);
  assert.deepEqual(mas("dresses"), ["D02", "D04"]);
  assert.deepEqual(mas("top knit"), mas("knit top"));
  assert.equal(mas("top knit").includes("A15"), true);
  assert.deepEqual(mas(""), BOOK.map((look) => look.ma));
});

test("loose mã matches only an existing mã and keeps leading zeros", () => {
  assert.equal(looseMaCandidate("a 15"), "A15");
  assert.equal(looseMaCandidate("a-15"), "A15");
  assert.equal(looseMaCandidate(" A15 "), "A15");
  assert.equal(looseMaCandidate("a015"), "A015");
  assert.deepEqual(mas("a 15"), ["A15"]);
  assert.deepEqual(mas("a-15"), ["A15"]);
  assert.deepEqual(mas(" A15 "), ["A15"]);
  assert.deepEqual(mas("a015"), []);
  assert.equal(mas("a015").includes("A15"), false);
  assert.deepEqual(mas("a015", WITH_PADDED), ["A015"]);
  assert.deepEqual(mas("a 15", WITH_PADDED), ["A15"]);
});

test("missing mã does not resolve to a product page", () => {
  assert.equal(exactMaLook(BOOK, "z99"), undefined);
  assert.equal(exactMaLook(BOOK, "a 99"), undefined);
  assert.equal(exactMaLook(BOOK, "a015"), undefined);
  assert.equal(resolveLookSearch(BOOK, "a 15").kind, "exact");
  assert.equal(lookSearchHref(resolveLookSearch(BOOK, "a 15")), "/m/A15");
  assert.equal(lookSearchHref(resolveLookSearch(BOOK, "a-15")), "/m/A15");
  assert.equal(lookSearchHref(resolveLookSearch(BOOK, " A15 ")), "/m/A15");
  assert.equal(resolveLookSearch(BOOK, "z99").kind, "results");
  assert.equal(resolveLookSearch(BOOK, "a 99").kind, "results");
  assert.equal(resolveLookSearch(BOOK, "a015").kind, "results");
  assert.equal(lookSearchHref(resolveLookSearch(BOOK, "z99")).startsWith("/m/"), false);
});

test("partial mã lists prefixes and suggestions stay capped", () => {
  const looks: LookSearchItem[] = [
    { ma: "A02", titleEn: "Knit top", titleVn: "Áo" },
    { ma: "A10", titleEn: "Lace tee", titleVn: "Áo ren" },
    { ma: "A11", titleEn: "Cardigan", titleVn: "Áo len" },
    { ma: "A12", titleEn: "Ruffle top", titleVn: "Áo bèo" },
    { ma: "A13", titleEn: "Kitten knit", titleVn: "Áo mèo" },
    { ma: "A14", titleEn: "Soft knit", titleVn: "Áo mềm" },
    { ma: "A15", titleEn: "Heather knit top", titleVn: "Áo len hoa" },
    { ma: "A16", titleEn: "Petal skirt", titleVn: "Chân váy" },
    { ma: "A17", titleEn: "Puppy sweater", titleVn: "Áo cún" },
    { ma: "A18", titleEn: "Magazine top", titleVn: "Áo tạp chí" },
    { ma: "A19", titleEn: "Bunny cardigan", titleVn: "Áo thỏ" },
    { ma: "D01", titleEn: "Pink dress", titleVn: "Đầm hồng" },
    { ma: "D02", titleEn: "Silk dress", titleVn: "Đầm lụa" },
    { ma: "D05", titleEn: "Lace dress", titleVn: "Đầm ren" },
    { ma: "S02", titleEn: "Two piece", titleVn: "Set đồ" },
    { ma: "S10", titleEn: "Pajama", titleVn: "Bộ ngủ" },
    { ma: "S11", titleEn: "Set two", titleVn: "Set hai" },
    { ma: "S12", titleEn: "Set three", titleVn: "Set ba" },
  ];
  assert.deepEqual(mas("a1", looks), ["A10", "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18", "A19"]);
  assert.deepEqual(mas("a 1", looks), mas("a1", looks));
  assert.deepEqual(mas("a-1", looks), mas("a1", looks));
  assert.deepEqual(mas("d0", looks), ["D01", "D02", "D05"]);
  assert.deepEqual(mas("s1", looks), ["S10", "S11", "S12"]);
  assert.deepEqual(mas("a 15", looks), ["A15"]);
  assert.deepEqual(mas("a-15", looks), ["A15"]);
  assert.deepEqual(mas("a015", looks), []);
  assert.equal(mas("a015", looks).includes("A15"), false);
  assert.equal(resolveLookSearch(looks, "a1").kind, "results");
  assert.equal(lookSearchHref(resolveLookSearch(looks, "a1")).startsWith("/m/"), false);
  const suggestions = suggestLooks(looks, "a1").map((look) => look.ma);
  assert.deepEqual(suggestions, ["A10", "A11", "A12", "A13", "A14", "A15", "A16", "A17"]);
  assert.equal(suggestions.length, 8);
});

test("search header stays capped at 80 characters", () => {
  const long = "a".repeat(120);
  assert.equal(decodeURIComponent(encodeShopSearchHeader(long)).length, 80);
});

test("search submit query is trimmed, capped at 80, and blank is skipped", () => {
  assert.equal(searchSubmitQuery("  A15  "), "A15");
  assert.equal(searchSubmitQuery("   "), null);
  assert.equal(searchSubmitQuery(""), null);
  assert.equal(searchSubmitQuery("áo".repeat(50))?.length, 80);
  assert.equal(searchSubmitQuery(`  ${"b".repeat(90)}  `), "b".repeat(80));
});
