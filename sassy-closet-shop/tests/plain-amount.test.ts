import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { intakeToPrefill, type IntakeSubmission } from "../lib/intake-import";
import { plainAmount } from "../lib/plain-amount";

const ACCEPTED: ReadonlyArray<readonly [string, number | null]> = [
  ["", null],
  ["40", 40],
  ["40.5", 40.5],
  ["40.", 40],
  ["25.00", 25],
  ["0", 0],
  ["1,200", 1200],
  ["1,200.50", 1200.5],
  ["100001", 100001],
  ["0.07", 0.07],
  ["  40  ", 40],
];

const REJECTED = [
  "2,5",
  "12,00",
  "0,025",
  "00,025",
  "0,000,025",
  "0,250",
  "01,025",
  "01,200",
  "1e2",
  "1E2",
  "0x10",
  "0x19",
  "-1",
  "+40",
  "$40",
  "2.5e1",
  "NaN",
  "Infinity",
  "70368744177664.01",
  "90071992547409.90",
];

function submission(overrides: Partial<IntakeSubmission>): IntakeSubmission {
  return {
    id: 0,
    ma: "",
    kind: "",
    size: "",
    color: "",
    color_note: "",
    pieces: [],
    link: "",
    price: "",
    cost_cny: "",
    cost_usd: "",
    cost_currency: "",
    sell_cny: "",
    sell_usd: "",
    sell_currency: "",
    blurb: "",
    photo_paths: [],
    photo_hashes: [],
    status: "",
    square: "",
    created_at: "",
    updated_at: "",
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: "",
    ...overrides,
  };
}

test("plain amounts keep digits, a trailing dot, and thousands commas", () => {
  for (const [raw, expected] of ACCEPTED) {
    assert.equal(plainAmount(raw), expected, JSON.stringify(raw));
  }
  assert.equal(plainAmount("1,200."), 1200);
  assert.equal(plainAmount("40.125"), 40.125);
});

test("plain amounts reject rewritten numbers", () => {
  for (const raw of REJECTED) {
    assert.equal(plainAmount(raw), null, raw);
  }
  assert.equal(plainAmount(".5"), null);
  assert.equal(plainAmount("40.5."), null);

  const shortComma = plainAmount("2,5");
  assert.equal(shortComma, null);
  assert.notEqual(shortComma, 25);

  const exponent = plainAmount("1e2");
  assert.equal(exponent, null);
  assert.notEqual(exponent, 100);

  const hex = plainAmount("0x19");
  assert.equal(hex, null);
  assert.notEqual(hex, 25);
});

test("calculator and intake call plainAmount without stripping every comma", () => {
  const calculator = readFileSync(new URL("../app/admin/price-calculator.tsx", import.meta.url), "utf8");
  const intake = readFileSync(new URL("../lib/intake-import.ts", import.meta.url), "utf8");
  for (const source of [calculator, intake]) {
    assert.equal(source.includes("plainAmount"), true);
    assert.equal(source.includes('.replace(/,/g, "")'), false);
  }
});

test("intake prefill keeps a thousands sell and drops rewritten amounts", () => {
  assert.equal(intakeToPrefill(submission({ sell_usd: "2,5" })).sellUsd, null);
  const exponent = ["1", "e2"].join("");
  const row = submission({});
  row.cost_cny = exponent;
  assert.equal(intakeToPrefill(row).costCny, null);
  assert.equal(intakeToPrefill(submission({ sell_usd: "1,200" })).sellUsd, 1200);
  assert.equal(intakeToPrefill(submission({ sell_usd: "25" })).sellUsd, 25);
});
