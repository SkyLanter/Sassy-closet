import assert from "node:assert/strict";
import test from "node:test";
import { intakePriceView, tieredSellUsd } from "../lib/pricing";

const FX = 6.723;

function digits(parts: string[]): string {
  return parts.join("");
}

const smallText = digits(["3", ".9"]);
const bumpedText = digits(["5", ".85"]);
const justAboveText = digits(["5", ".86"]);
const sixText = digits(["6"]);
const highTenText = digits(["6", ".49"]);
const exactTenText = digits(["6", ".5"]);
const justOverText = digits(["6", ".51"]);

test("the tiered quote adds $2 only when the ceil is under $10", () => {
  assert.equal(tieredSellUsd(Number(smallText)), 8);
  assert.equal(tieredSellUsd(Number(bumpedText)), 11);
  assert.equal(tieredSellUsd(Number(justAboveText)), 10);
  assert.equal(tieredSellUsd(Number(sixText)), 10);
  assert.equal(tieredSellUsd(Number(highTenText)), 10);
  assert.equal(tieredSellUsd(Number(exactTenText)), 10);
  assert.equal(tieredSellUsd(Number(justOverText)), 11);
});

test("a blank sell shows that tier, including a bump under $10 and a ceil of $10", () => {
  const low = intakePriceView({
    ma: "A08",
    kind: "A",
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: smallText,
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(low.dollars, 8);
  assert.equal(low.label, "$8");
  assert.equal(low.flag, "ok");

  const atSix = intakePriceView({
    ma: "A09",
    kind: "A",
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: sixText,
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(atSix.dollars, 10);
  assert.equal(atSix.label, "$10");
  assert.equal(atSix.flag, "ok");

  const atTen = intakePriceView({
    ma: "A10",
    kind: "A",
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: exactTenText,
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(atTen.dollars, 10);
  assert.equal(atTen.label, "$10");
  assert.equal(atTen.flag, "ok");
});
