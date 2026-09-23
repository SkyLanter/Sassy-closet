import assert from "node:assert/strict";
import { test } from "node:test";
import {
  intakeToPrefill,
  parseIntakeImportJson,
  sanitizeIntakeSubmission,
} from "../lib/intake-import";

function stagedRow(overrides: Record<string, unknown> = {}) {
  return {
    id: 1,
    ma: "A24",
    kind: "A",
    size: "S M",
    color: "Đen",
    color_note: "",
    pieces: [],
    link: "https://item.taobao.com/item.htm?id=123",
    price: "",
    cost_cny: "68",
    cost_usd: "",
    cost_currency: "CNY",
    sell_cny: "",
    sell_usd: "",
    sell_currency: "USD",
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

test("sanitizeIntakeSubmission carries the needs_research flag (#53)", () => {
  const flagged = sanitizeIntakeSubmission(stagedRow({ needs_research: true }));
  assert.ok(flagged);
  assert.equal(flagged.needsResearch, true);

  const clean = sanitizeIntakeSubmission(stagedRow({ needs_research: false }));
  assert.ok(clean);
  assert.equal(clean.needsResearch, false);

  // Older rows predate #53 — a missing flag means "not flagged", never an error.
  const legacy = sanitizeIntakeSubmission(stagedRow());
  assert.ok(legacy);
  assert.equal(legacy.needsResearch, false);
});

test("intakeToPrefill warns when the intake submission needs research", () => {
  const flagged = sanitizeIntakeSubmission(stagedRow({ needs_research: true }));
  assert.ok(flagged);
  const prefill = intakeToPrefill(flagged);
  assert.equal(prefill.needsResearch, true);
  assert.ok(
    prefill.warnings.some((warning) => /needs research/i.test(warning)),
    `expected a needs-research warning, got: ${JSON.stringify(prefill.warnings)}`,
  );

  const clean = sanitizeIntakeSubmission(stagedRow({}));
  assert.ok(clean);
  const cleanPrefill = intakeToPrefill(clean);
  assert.equal(cleanPrefill.needsResearch, false);
  assert.ok(
    cleanPrefill.warnings.every((warning) => !/needs research/i.test(warning)),
    "no needs-research warning when the flag is absent",
  );
});

test("parseIntakeImportJson keeps needs_research through the paste path", () => {
  const parsed = parseIntakeImportJson(JSON.stringify(stagedRow({ needs_research: true })));
  assert.equal(parsed.ok, true);
  if (parsed.ok) {
    assert.equal(parsed.submissions.length, 1);
    assert.equal(parsed.submissions[0].needsResearch, true);
  }
});
