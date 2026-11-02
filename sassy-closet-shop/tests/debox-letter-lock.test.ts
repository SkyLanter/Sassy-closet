import assert from "node:assert/strict";
import test from "node:test";
import { calcPricing, deboxForLetter, FX_DEFAULT } from "../lib/pricing";

function digits(parts: string[]): string {
  return parts.join("");
}

test("dress letters keep the locked debox in any case, and other letters stay unknown", () => {
  for (const letter of ["V", "v", " Q ", "q", "d", "D"]) {
    assert.equal(deboxForLetter(letter), 7.5, letter);
  }
  for (const letter of ["A", "a", " S ", "G", ""]) {
    assert.equal(deboxForLetter(letter), null, JSON.stringify(letter));
  }
});

test("the locked dress debox is what the flat quote adds", () => {
  const goods = Number(digits(["1", "0"]));
  const debox = deboxForLetter("v");
  assert.equal(debox, 7.5);
  const priced = calcPricing({
    costCny: null,
    costUsd: goods,
    fx: FX_DEFAULT,
    deboxUsd: debox,
  });
  assert.equal(priced.landedUsd, goods + 7.5);
  assert.equal(priced.sellUsd, 24);

  const unknown = calcPricing({
    costCny: null,
    costUsd: goods,
    fx: FX_DEFAULT,
    deboxUsd: deboxForLetter("a"),
  });
  assert.equal(unknown.sellUsd, null);
  assert.equal(unknown.landedUsd, null);
});
