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

test("search header stays capped at 80 characters", () => {
  const long = "a".repeat(120);
  assert.equal(decodeURIComponent(encodeShopSearchHeader(long)).length, 80);
});
