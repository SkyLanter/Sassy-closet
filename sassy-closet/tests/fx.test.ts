import assert from "node:assert/strict";
import { test } from "node:test";
import { convertCnyToUsd, convertUsdToCny, formatMoney } from "../lib/fx";
import { KIND_CODES, kindLabel } from "../lib/kinds";
import { nextMa, parseHubMa } from "../lib/mint";

const WEEKLY = 6.71;

test("kind D is Đầm / Dress and V stays Váy", () => {
  assert.ok(KIND_CODES.includes("D"));
  assert.ok(KIND_CODES.includes("V"));
  assert.equal(kindLabel("D"), "Đầm / Dress");
  assert.equal(kindLabel("V"), "Váy");
  assert.deepEqual(parseHubMa("D01"), { kind: "D", n: 1 });
  assert.equal(nextMa("D", []), "D01");
  assert.equal(nextMa("D", ["D01", "V01"]), "D02");
  assert.equal(parseHubMa("X01"), null);
});

test("CNY↔USD convert both ways on the weekly rate", () => {
  assert.equal(convertCnyToUsd("80", WEEKLY), formatMoney(80 / WEEKLY));
  assert.equal(convertUsdToCny("12", WEEKLY), formatMoney(12 * WEEKLY));
  assert.equal(convertCnyToUsd("80", WEEKLY), "11.92");
  assert.equal(convertUsdToCny("12", WEEKLY), "80.52");
  assert.equal(convertCnyToUsd("", WEEKLY), "");
  assert.equal(convertUsdToCny("", WEEKLY), "");
  assert.equal(convertCnyToUsd(".", WEEKLY), null);
  assert.equal(convertUsdToCny("abc", WEEKLY), null);
  assert.equal(convertCnyToUsd("80", 0), null);
  assert.equal(convertUsdToCny("12", Number.NaN), null);
});
