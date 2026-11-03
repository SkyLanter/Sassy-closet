import assert from "node:assert/strict";
import test from "node:test";
import { calcPricing, FX_DEFAULT, MARGIN_DIVISOR, quoteSellUsd } from "../lib/pricing";

function digits(parts: string[]): string {
  return parts.join("");
}

const ceilNine = Number(digits(["6", ".75"]));
const tenLow = Number(digits(["6", ".76"]));
const tenMid = Number(digits(["7"]));
const tenHigh = Number(digits(["7", ".49"]));
const exactTen = Number(digits(["7", ".5"]));
const eleven = Number(digits(["7", ".51"]));

test("the flat quote adds $2 only when the ceil is under $10", () => {
  for (let quoted = 1; quoted <= 9; quoted += 1) {
    const landed = quoted * MARGIN_DIVISOR;
    const quote = quoteSellUsd(landed);
    assert.equal(quote.quotedUsd, quoted, String(quoted));
    assert.equal(quote.sellUsd, quoted + 2, String(quoted));
  }
  assert.equal(quoteSellUsd(ceilNine).quotedUsd, 9);
  assert.equal(quoteSellUsd(ceilNine).sellUsd, 11);
  assert.equal(quoteSellUsd(tenLow).quotedUsd, 10);
  assert.equal(quoteSellUsd(tenLow).sellUsd, 10);
  assert.equal(quoteSellUsd(tenMid).sellUsd, 10);
  assert.equal(quoteSellUsd(tenHigh).sellUsd, 10);
  assert.equal(quoteSellUsd(exactTen).quotedUsd, 10);
  assert.equal(quoteSellUsd(exactTen).sellUsd, 10);
  assert.equal(quoteSellUsd(eleven).quotedUsd, 11);
  assert.equal(quoteSellUsd(eleven).sellUsd, 11);
});

test("a goods cost plus debox that lands on $7.50 still sells at $10", () => {
  const goods = Number(digits(["5"]));
  const debox = Number(digits(["2", ".5"]));
  const priced = calcPricing({
    costCny: null,
    costUsd: goods,
    fx: FX_DEFAULT,
    deboxUsd: debox,
  });
  assert.equal(priced.landedUsd, exactTen);
  assert.equal(priced.sellUsd, 10);
});
