import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { TYPE_LABELS } from "../lib/catalog";
import { MA_LETTERS, type MaLetter } from "../lib/ma";
import { suggestOutfitBundle } from "../lib/outfit-bundle";

const NAMED: Record<"S" | "A" | "D" | "Q", { piece: MaLetter; pieceEn: string }> = {
  S: { piece: "G", pieceEn: "Shoes" },
  A: { piece: "Q", pieceEn: "Pants" },
  D: { piece: "G", pieceEn: "Shoes" },
  Q: { piece: "A", pieceEn: "Top" },
};

test("S, A, D, and Q each suggest one complementary piece type", () => {
  for (const letter of ["S", "A", "D", "Q"] as const) {
    const suggestion = suggestOutfitBundle(letter);
    assert.ok(suggestion);
    assert.equal(suggestion.letter, letter);
    assert.equal(suggestion.piece, NAMED[letter].piece);
    assert.equal(suggestion.pieceEn, NAMED[letter].pieceEn);
    assert.equal(suggestion.pieceVn, TYPE_LABELS[suggestion.piece].vn);
    assert.equal(suggestion.piece.length, 1);
    assert.notEqual(suggestion.piece, letter);
  }
});

test("every catalog letter suggests one other catalog letter", () => {
  const seen = new Set<string>();
  for (const letter of MA_LETTERS) {
    const suggestion = suggestOutfitBundle(letter);
    assert.ok(suggestion, letter);
    assert.equal(suggestion.letter, letter);
    assert.equal(MA_LETTERS.includes(suggestion.piece), true);
    assert.notEqual(suggestion.piece, letter);
    assert.equal(suggestion.pieceEn, TYPE_LABELS[suggestion.piece].en);
    assert.equal(suggestion.pieceVn, TYPE_LABELS[suggestion.piece].vn);
    assert.equal(/^[A-Z]\d/.test(suggestion.piece), false);
    seen.add(letter);
  }
  assert.equal(seen.size, MA_LETTERS.length);
  assert.deepEqual(
    [...seen],
    ["A", "Q", "V", "D", "K", "G", "B", "P", "H", "J", "S", "O"],
  );
});

test("a lowercase letter matches and a mã or unknown letter does not", () => {
  assert.equal(suggestOutfitBundle("s")?.piece, "G");
  assert.equal(suggestOutfitBundle(" a ")?.piece, "Q");
  for (const input of ["S06", "A01", "Q02", "K06", "V05", "X", "", "SS", "1"]) {
    assert.equal(suggestOutfitBundle(input), null, input);
  }
});

test("seed catalog types get a piece type and S06 is not repriced", () => {
  const source = readFileSync(path.join(process.cwd(), "lib/outfit-bundle.ts"), "utf8");
  assert.equal(source.includes("S06"), false);
  assert.equal(source.includes("priceUsd"), false);
  assert.equal(source.includes("held.json"), false);

  const doc = JSON.parse(readFileSync(path.join(process.cwd(), "data/products.json"), "utf8")) as {
    products: Array<{ ma: string; type: string; priceUsd: number | null }>;
  };
  const types = new Set<string>();
  for (const product of doc.products) {
    types.add(product.type);
    const suggestion = suggestOutfitBundle(product.type);
    assert.ok(suggestion, product.ma);
    assert.equal(suggestion.piece.length, 1);
    assert.notEqual(suggestion.piece, product.ma);
    if (product.ma === "S06") {
      assert.equal(product.priceUsd, 25);
    }
  }
  for (const letter of ["S", "A", "D", "Q"]) {
    assert.equal(types.has(letter), true);
  }
});
