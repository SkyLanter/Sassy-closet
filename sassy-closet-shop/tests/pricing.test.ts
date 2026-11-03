import assert from "node:assert/strict";
import test from "node:test";
import {
  calcPricing,
  FX_DEFAULT,
  MARGIN_DIVISOR,
  MARGIN_TARGET,
  quoteSellUsd,
  UNDER_TEN_BUMP_USD,
  UNDER_TEN_LIMIT_USD,
} from "../lib/pricing";

test("admin price: sell = ceil(landed / 0.75) at 25% margin", () => {
  assert.equal(MARGIN_TARGET, 0.25);
  assert.equal(MARGIN_DIVISOR, 0.75);
  const breakdown = calcPricing({
    costCny: 53.78,
    costUsd: null,
    fx: FX_DEFAULT,
    deboxUsd: 7.5,
  });
  assert.equal(breakdown.landedUsd !== null, true);
  const landed = breakdown.landedUsd as number;
  assert.ok(Math.abs(landed - (53.78 / FX_DEFAULT + 7.5)) < 1e-9);
  assert.equal(breakdown.sellUsd, quoteSellUsd(landed).sellUsd);
  assert.equal(breakdown.sellUsd, 21);
});

test("admin price: ceil under $10 adds $2", () => {
  const breakdown = calcPricing({
    costCny: 30,
    costUsd: null,
    fx: FX_DEFAULT,
    deboxUsd: 0.01,
  });
  const landed = breakdown.landedUsd as number;
  const quoted = quoteSellUsd(landed);
  assert.ok(quoted.quotedUsd < UNDER_TEN_LIMIT_USD);
  assert.equal(quoted.sellUsd, quoted.quotedUsd + UNDER_TEN_BUMP_USD);
  assert.equal(breakdown.sellUsd, quoted.sellUsd);
});
