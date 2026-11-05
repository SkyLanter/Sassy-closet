import assert from "node:assert/strict";
import test from "node:test";
import { intakeToPrefill, prefillToDraft, type IntakeSubmission } from "../lib/intake-import";

function submission(overrides: Partial<IntakeSubmission>): IntakeSubmission {
  return {
    id: 0,
    ma: "G02",
    kind: "G",
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
    status: "staged",
    square: "not_square",
    created_at: "",
    updated_at: "",
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: "",
    ...overrides,
  };
}

test("kind G keeps exact EU chips and one trailing .0 on 35–41", () => {
  const prefill = intakeToPrefill(submission({ size: "37 38" }));
  assert.deepEqual(prefill.sizes, ["37", "38"]);
  assert.deepEqual(prefill.droppedSizes, []);
  assert.equal(prefill.warnings.some((warning) => warning.includes("never invent")), false);

  const folded = intakeToPrefill(submission({ kind: "g", size: "35.0, 36" }));
  assert.deepEqual(folded.sizes, ["35", "36"]);
  assert.deepEqual(folded.droppedSizes, []);

  const exactEnds = intakeToPrefill(submission({ size: "34 42" }));
  assert.deepEqual(exactEnds.sizes, ["34", "42"]);

  const deduped = intakeToPrefill(submission({ size: "35 35.0" }));
  assert.deepEqual(deduped.sizes, ["35"]);

  const withLetter = intakeToPrefill(submission({ size: "S 38" }));
  assert.deepEqual(withLetter.sizes, ["S", "38"]);
});

test("kind G drops tokens that are not an exact chip", () => {
  const prefill = intakeToPrefill(
    submission({ size: "35.00 34.0 42.0 34.5 40. 40码 EU40 35-36" }),
  );
  assert.deepEqual(prefill.sizes, []);
  assert.deepEqual(prefill.droppedSizes, ["35.00", "34.0", "42.0", "34.5", "40.", "40码", "EU40", "35-36"]);
  assert.equal(prefill.warnings.some((warning) => warning.includes("never invent")), true);
});

test("clothing sizes stay letters and a shoe number is not invented", () => {
  const clothing = intakeToPrefill(submission({ ma: "A02", kind: "A", size: "40 35.0 M" }));
  assert.deepEqual(clothing.sizes, ["M"]);
  assert.deepEqual(clothing.droppedSizes, ["40", "35.0"]);

  const other = intakeToPrefill(submission({ ma: "O01", kind: "O", size: "38" }));
  assert.deepEqual(other.sizes, []);
  assert.deepEqual(other.droppedSizes, ["38"]);
});

test("a shoe import stays a hold draft with no price", () => {
  const draft = prefillToDraft(intakeToPrefill(submission({ size: "37 38", sell_usd: "26" })));
  assert.equal(draft.status, "hold");
  assert.equal(draft.priceInput, "");
  assert.deepEqual(draft.sizes, ["37", "38"]);
});

test("kind with surrounding spaces keeps shoe 38 and the draft stays an unpriced hold", () => {
  const prefill = intakeToPrefill(submission({ kind: " G ", size: "38", sell_usd: "26" }));
  assert.equal(prefill.letter, "G");
  assert.deepEqual(prefill.sizes, ["38"]);
  assert.deepEqual(prefill.droppedSizes, []);
  assert.equal(prefill.warnings.some((warning) => warning.includes("never invent")), false);

  const draft = prefillToDraft(prefill);
  assert.equal(draft.status, "hold");
  assert.equal(draft.priceInput, "");
  assert.deepEqual(draft.sizes, ["38"]);
});
