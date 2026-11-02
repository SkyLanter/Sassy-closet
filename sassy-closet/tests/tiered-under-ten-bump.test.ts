import assert from "node:assert/strict";
import test from "node:test";
import { intakePriceView, tieredSellUsd } from "../lib/pricing";

const FX = 6.723;

function digits(parts: string[]): string {
  return parts.join("");
}

const small = Number(digits(["3", ".9"]));
const bumped = Number(digits(["5", ".85"]));
const exactTen = Number(digits(["6", ".5"]));
const justOver = Number(digits(["6", ".51"]));

test("the tiered quote adds $2 only when the ceil is under $10", () => {
  assert.equal(tieredSellUsd(small), 8);
  assert.equal(tieredSellUsd(bumped), 11);
  assert.equal(tieredSellUsd(exactTen), 10);
  assert.equal(tieredSellUsd(justOver), 11);
});

test("a blank sell shows that tier, including a bump under $10 and a ceil of $10", () => {
  const low = intakePriceView({
    ma: "A08",
    kind: "A",
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: digits(["3", ".9"]),
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(low.dollars, 8);
  assert.equal(low.label, "$8");
  assert.equal(low.flag, "ok");

  const atTen = intakePriceView({
    ma: "A09",
    kind: "A",
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: "",
    costUsd: digits(["6", ".5"]),
    costCurrency: "USD",
    fxRate: FX,
  });
  assert.equal(atTen.dollars, 10);
  assert.equal(atTen.label, "$10");
  assert.equal(atTen.flag, "ok");
});
