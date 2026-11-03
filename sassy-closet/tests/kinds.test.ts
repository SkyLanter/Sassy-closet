import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { test } from "node:test";
import {
  KIND_CODES,
  KINDS,
  SHOE_SIZES,
  intakeCatalog,
  keepSizesForKind,
  kindLabel,
  restoreSizes,
  sizeOptionsLine,
  sizeScaleForKind,
  sizesForKind,
} from "../lib/kinds";

test("kind letters stay the full mã set including D, G, H, J", () => {
  assert.deepEqual(KIND_CODES, ["A", "Q", "V", "D", "K", "G", "B", "P", "H", "J", "S", "O"]);
  assert.deepEqual(
    KINDS.map((kind) => kind.code),
    [...KIND_CODES],
  );
});

test("G H J D labels and size rules match intake catalog", () => {
  assert.equal(kindLabel("D"), "Đầm / Dress");
  assert.equal(kindLabel("G"), "Giày / Cao gót");
  assert.equal(kindLabel("H"), "Phụ kiện tóc / Hair accessories");
  assert.equal(kindLabel("J"), "Trang sức / Jewelry");
  assert.ok(!/^Tóc$/.test(kindLabel("H")));
  assert.ok(!/^Hair$/.test(kindLabel("H")));
  assert.equal(sizeScaleForKind("G"), "shoe");
  assert.deepEqual([...sizesForKind("G")], ["35", "36", "37", "38", "39", "40", "41"]);
  assert.deepEqual([...sizesForKind("A")], ["2XS", "XS", "S", "M", "L", "XL", "2XL"]);
  assert.deepEqual([...sizesForKind("D")], [...sizesForKind("A")]);
  assert.deepEqual([...sizesForKind("H")], [...sizesForKind("A")]);
  assert.deepEqual([...sizesForKind("J")], [...sizesForKind("A")]);
  assert.equal(sizeOptionsLine("G"), SHOE_SIZES.join(" "));
  assert.deepEqual(keepSizesForKind(["M", "38", "2XS"], "G"), ["38"]);
  assert.deepEqual(keepSizesForKind(["M", "38", "2XS"], "A"), ["M", "2XS"]);
});

test("keepSizesForKind folds one trailing .0 onto a real chip and drops the rest", () => {
  assert.deepEqual(keepSizesForKind(["35.0", "36"], "G"), ["35", "36"]);
  assert.deepEqual(keepSizesForKind(["40.0"], "A"), []);
  assert.deepEqual(keepSizesForKind(["40.00"], "G"), []);
  assert.deepEqual(keepSizesForKind(["34.0", "42.0"], "G"), []);
  assert.deepEqual(keepSizesForKind(["35.00"], "G"), []);
  assert.deepEqual(keepSizesForKind(["40."], "G"), []);
  assert.deepEqual(keepSizesForKind(["5.0"], "G"), []);
  assert.deepEqual(keepSizesForKind(["100.0"], "G"), []);
  assert.deepEqual(keepSizesForKind(["35.0", "35"], "G"), ["35"]);
});

test("restoreSizes splits saved size text and keeps non-chip tokens", () => {
  assert.deepEqual(restoreSizes("35;36|37", "G"), ["35", "36", "37"]);
  assert.deepEqual(restoreSizes("35.0 36", "G"), ["35", "36"]);
  assert.deepEqual(restoreSizes(";;;", "G"), []);
  assert.deepEqual(restoreSizes("均码", "G"), ["均码"]);
  assert.deepEqual(restoreSizes("40.0", "A"), ["40.0"]);
  assert.deepEqual(restoreSizes("35.0 35", "G"), ["35"]);
  assert.deepEqual(restoreSizes("35-36", "G"), ["35-36"]);
  assert.deepEqual(restoreSizes("35/36", "G"), ["35", "36"]);
  assert.deepEqual(restoreSizes("XXS", "A"), ["XXS"]);
  assert.deepEqual(restoreSizes("  35.0  ", "G"), ["35"]);
});

test("applySubmission restores the saved size through restoreSizes", () => {
  const src = fs.readFileSync(path.join(process.cwd(), "components", "IntakeApp.tsx"), "utf8");
  const start = src.indexOf("function applySubmission(");
  const end = src.indexOf("async function save(", start);
  assert.ok(start >= 0, "applySubmission not found");
  assert.ok(end > start, "applySubmission slice must stop before save()");
  const apply = src.slice(start, end);
  assert.match(apply, /setSizes\(restoreSizes\(item\.size,\s*item\.kind\)\)/);
  assert.equal(apply.includes("split(/[\\s,]+/)"), false);
});

test("catalog dataset carries kind label + size options without inventing mã", () => {
  const catalog = intakeCatalog();
  const byCode = Object.fromEntries(catalog.kinds.map((kind) => [kind.code, kind]));
  assert.equal(catalog.kinds.length, KIND_CODES.length);
  assert.equal(byCode.G.label, "Giày / Cao gót");
  assert.deepEqual(byCode.G.sizes, [...SHOE_SIZES]);
  assert.equal(byCode.H.label, "Phụ kiện tóc / Hair accessories");
  assert.equal(byCode.J.label, "Trang sức / Jewelry");
  assert.equal(byCode.D.label, "Đầm / Dress");
  assert.ok(!catalog.kinds.some((kind) => kind.code === "X"));
});
