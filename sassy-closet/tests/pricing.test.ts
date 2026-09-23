import assert from "node:assert/strict";
import { test } from "node:test";
import {
  captionPriceLine,
  computeAutoPrice,
  deboxFor,
  DEFAULT_FX,
  MARGIN_FLOOR,
  TARGET_MARGIN,
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

test("auto price: sell = ceil(landed / 0.7) with landed = CNY/FX + debox", () => {
  // V03-style: ¥53.78 at FX 6.723 + $7.50 debox -> landed $15.50, sell ceil(22.14) = 23
  const breakdown = computeAutoPrice({ costCny: 53.78, fxRate: FX, kind: "V" });
  assert.ok(breakdown);
  assert.equal(breakdown.deboxUsd, 7.5);
  assert.ok(Math.abs(breakdown.landedUsd - (53.78 / FX + 7.5)) < 1e-9);
  assert.equal(breakdown.sellUsd, Math.ceil(breakdown.landedUsd / (1 - TARGET_MARGIN)));
  assert.equal(breakdown.sellUsd, 23);
  assert.ok(Math.abs(breakdown.marginPct - 0.3) < 0.05); // ceil bumps margin a touch
  assert.equal(breakdown.captionEligible, breakdown.marginPct >= MARGIN_FLOOR);
});

test("auto price returns null for bad inputs instead of inventing a price", () => {
  assert.equal(computeAutoPrice({ costCny: 0, fxRate: FX, kind: "A" }), null);
  assert.equal(computeAutoPrice({ costCny: NaN, fxRate: FX, kind: "A" }), null);
  assert.equal(computeAutoPrice({ costCny: 50, fxRate: 0, kind: "A" }), null);
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
