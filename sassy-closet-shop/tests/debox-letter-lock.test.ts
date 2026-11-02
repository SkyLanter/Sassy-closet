import assert from "node:assert/strict";
import test from "node:test";
import { MA_LETTERS } from "../lib/ma";
import { calcPricing, deboxForLetter, FX_DEFAULT } from "../lib/pricing";

const LOCKED_DEBOX = new Set(["V", "Q", "D"]);

function digits(parts: string[]): string {
  return parts.join("");
}

test("only V, Q, and D keep the locked debox, in any case or spacing", () => {
  for (const letter of MA_LETTERS) {
    const expected = LOCKED_DEBOX.has(letter) ? 7.5 : null;
    assert.equal(deboxForLetter(letter), expected, letter);
    assert.equal(deboxForLetter(letter.toLowerCase()), expected, letter.toLowerCase());
    assert.equal(deboxForLetter(` ${letter.toLowerCase()} `), expected, letter);
  }
  assert.equal(deboxForLetter(""), null);
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
