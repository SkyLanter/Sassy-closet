import assert from "node:assert/strict";
import { test } from "node:test";
import {
  captionPriceLine,
  intakePriceView,
  sellPriceFlag,
  tieredSellUsd,
  computeAutoPrice,
  deboxFor,
  DEFAULT_FX,
  MARGIN_FLOOR,
  TARGET_MARGIN,
  UNDER_TEN_BUMP_USD,
  UNDER_TEN_LIMIT_USD,
} from "../lib/pricing";

const FX = 6.723;

test("debox is locked at $7.50 for V/Q/D and ignores overrides", () => {
  assert.equal(deboxFor("V"), 7.5);
  assert.equal(deboxFor("Q"), 7.5);
  assert.equal(deboxFor("D"), 7.5);
  assert.equal(deboxFor("V", { V: 0 }), 7.5);
  assert.equal(deboxFor("Q", { Q: 99 }), 7.5);
});

test("debox defaults to $0 for other letters unless Boss sets a value", () => {
  assert.equal(deboxFor("A"), 0);
  assert.equal(deboxFor("K", { K: 3 }), 3);
  assert.equal(deboxFor("A", { K: 3 }), 0);
  assert.equal(deboxFor("G", { G: -1 }), 0);
});

test("auto price: sell = ceil(landed / 0.75) with landed = CNY/FX + debox", () => {
  // V03-style: ¥53.78 at FX 6.723 + $7.50 debox -> landed $15.50, sell ceil(20.67) = 21
  const breakdown = computeAutoPrice({ costCny: 53.78, fxRate: FX, kind: "V" });
  assert.ok(breakdown);
  assert.equal(breakdown.deboxUsd, 7.5);
  assert.ok(Math.abs(breakdown.landedUsd - (53.78 / FX + 7.5)) < 1e-9);
  assert.equal(breakdown.sellUsd, Math.ceil(breakdown.landedUsd / (1 - TARGET_MARGIN)));
  assert.equal(breakdown.sellUsd, 21);
  assert.ok(Math.abs(breakdown.marginPct - 0.25) < 0.05); // ceil bumps margin a touch
  assert.equal(breakdown.captionEligible, breakdown.marginPct >= MARGIN_FLOOR);
});

test("auto price: ceil under $10 adds $2", () => {
  // landed = 30/6.723 ≈ $4.46; ceil(4.46/0.75) = 6; 6 < $10 so sell = 8
  const breakdown = computeAutoPrice({ costCny: 30, fxRate: FX, kind: "A" });
  assert.ok(breakdown);
  const quoted = Math.ceil(breakdown.landedUsd / (1 - TARGET_MARGIN));
  assert.ok(quoted < UNDER_TEN_LIMIT_USD);
  assert.equal(breakdown.sellUsd, quoted + UNDER_TEN_BUMP_USD);
  assert.equal(breakdown.sellUsd, 8);
});

test("auto price: ceil at $10 does not add $2", () => {
  // landed = 50/6.723 ≈ $7.44; ceil(7.44/0.75) = 10
  const breakdown = computeAutoPrice({ costCny: 50, fxRate: FX, kind: "A" });
  assert.ok(breakdown);
  assert.equal(Math.ceil(breakdown.landedUsd / (1 - TARGET_MARGIN)), 10);
  assert.equal(breakdown.sellUsd, 10);
});

test("auto price returns null for bad inputs instead of inventing a price", () => {
  assert.equal(computeAutoPrice({ costCny: 0, fxRate: FX, kind: "A" }), null);
  assert.equal(computeAutoPrice({ costCny: NaN, fxRate: FX, kind: "A" }), null);
  assert.equal(computeAutoPrice({ costCny: 50, fxRate: 0, kind: "A" }), null);
});

test("tiered sell matches auto-list fixed points", () => {
  assert.equal(tieredSellUsd(16.26), 26);
  assert.equal(tieredSellUsd(19.5), 30);
  assert.equal(tieredSellUsd(19.51), 30);
  assert.equal(tieredSellUsd(19.58), 30);
  assert.equal(tieredSellUsd(30), 42);
  assert.equal(tieredSellUsd(33), 45);
  assert.equal(tieredSellUsd(0), null);
});

test("blank sell with cost shows the calculated dollar, not calculate-later", () => {
  const view = intakePriceView({
    ma: "A01",
    kind: "A",
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: "16.26",
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(view.label, "$26");
  assert.equal(view.flag, "ok");
  assert.notEqual(view.label, "Tính giá sau");
});

test("a calculated sell under the 35% floor is flagged and still shown", () => {
  const view = intakePriceView({
    ma: "A04",
    kind: "A",
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: "33",
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(view.label, "$45");
  assert.equal(view.flag, "under-margin");
});

test("blank sell without cost stays calculate-later", () => {
  const view = intakePriceView({
    ma: "A02",
    kind: "A",
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: "",
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(view.flag, "later");
  assert.equal(view.label, "Tính giá sau");
});

test("S06 blank sell stays $25", () => {
  const view = intakePriceView({
    ma: "s6",
    kind: "S",
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "80",
    costUsd: "12",
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(view.dollars, 25);
  assert.equal(view.label, "$25");
  assert.equal(view.flag, "ok");
});

test("a typed sell under the tiered quote is flagged and still priced", () => {
  const view = intakePriceView({
    ma: "A03",
    kind: "A",
    sellUsd: "20",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: "16.26",
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(view.label, "$20");
  assert.equal(view.flag, "under-margin");
});

test("blank sell is later, not a forced price", () => {
  const input = {
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "50",
    costUsd: "",
    costCurrency: "CNY",
    kind: "A",
    fxRate: FX,
  };
  assert.equal(sellPriceFlag(input), "later");
  assert.equal(captionPriceLine(input), "Inbox giá");
});

test("typed sell under the margin floor is flagged", () => {
  const input = {
    sellUsd: "10",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "50",
    costUsd: "",
    costCurrency: "CNY",
    kind: "A",
    fxRate: FX,
  };
  assert.equal(sellPriceFlag(input), "under-margin");
});

test("typed sell at the margin floor is ok", () => {
  const input = {
    sellUsd: "12",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "50",
    costUsd: "",
    costCurrency: "CNY",
    kind: "A",
    fxRate: FX,
  };
  assert.equal(sellPriceFlag(input), "ok");
});

test("caption price: blank sell stays Inbox giá", () => {
  const base = {
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "50",
    costUsd: "",
    costCurrency: "CNY",
    kind: "A",
    fxRate: FX,
  };
  assert.equal(captionPriceLine(base), "Inbox giá");
});

test("caption price: margin under 35% floor stays Inbox giá", () => {
  // landed = 50/6.723 = $7.44; sell $10 -> margin 25.6% < 35%
  const line = captionPriceLine({
    sellUsd: "10",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "50",
    costUsd: "",
    costCurrency: "CNY",
    kind: "A",
    fxRate: FX,
  });
  assert.equal(line, "Inbox giá");
});

test("caption price: margin at/above 35% shows the price", () => {
  // landed = $7.44; sell $12 -> margin 38% >= 35%
  const line = captionPriceLine({
    sellUsd: "12",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "50",
    costUsd: "",
    costCurrency: "CNY",
    kind: "A",
    fxRate: FX,
  });
  assert.equal(line, "$12");
});

test("caption price: unknown cost does not block a set sell price", () => {
  const line = captionPriceLine({
    sellUsd: "24",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: "",
    costCurrency: "USD",
    kind: "V",
    fxRate: DEFAULT_FX,
  });
  assert.equal(line, "$24");
});

test("caption price: CNY sell shows ¥ when eligible", () => {
  const line = captionPriceLine({
    sellUsd: "",
    sellCny: "100",
    sellCurrency: "CNY",
    costCny: "30",
    costUsd: "",
    costCurrency: "CNY",
    kind: "A",
    fxRate: FX,
  });
  assert.equal(line, "¥100");
});
