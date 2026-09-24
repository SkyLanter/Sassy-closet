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

test("sanitizeIntakeSubmission carries auto_price and taobao_snapshot (#53)", () => {
  const row = stagedRow({
    auto_price: {
      landedUsd: 17.6,
      deboxUsd: 7.5,
      sellUsd: 26,
      marginUsd: 8.4,
      marginPct: 0.32,
      captionEligible: false,
    },
    taobao_snapshot: {
      itemId: "123",
      title: "Puppy cardigan",
      listCny: "68",
      promoCny: null,
      colors: ["黑色", "白色"],
    },
  });
  const submission = sanitizeIntakeSubmission(row);
  assert.ok(submission);
  assert.equal(submission.autoPrice?.sellUsd, 26);
  assert.equal(submission.autoPrice?.landedUsd, 17.6);
  assert.equal(submission.taobaoSnapshot?.itemId, "123");
  assert.equal(submission.taobaoSnapshot?.title, "Puppy cardigan");
  assert.deepEqual(submission.taobaoSnapshot?.colors, ["黑色", "白色"]);

  const prefill = intakeToPrefill(submission);
  assert.equal(prefill.autoPrice?.sellUsd, 26);
  assert.equal(prefill.taobaoSnapshot?.listCny, "68");
  assert.ok(
    prefill.warnings.some((warning) => /\$26/.test(warning)),
    `expected an auto-price warning naming $26, got: ${JSON.stringify(prefill.warnings)}`,
  );

  // Legacy rows without the fields stay null — never an error.
  const legacy = sanitizeIntakeSubmission(stagedRow());
  assert.ok(legacy);
  assert.equal(legacy.autoPrice, null);
  assert.equal(legacy.taobaoSnapshot, null);
  const legacyPrefill = intakeToPrefill(legacy);
  assert.equal(legacyPrefill.autoPrice, null);
  assert.equal(legacyPrefill.taobaoSnapshot, null);
});

test("sanitizeIntakeSubmission drops malformed auto_price/taobao_snapshot", () => {
  const bad = sanitizeIntakeSubmission(
    stagedRow({
      auto_price: { sellUsd: "twenty-six" },
      taobao_snapshot: { title: "no item id" },
    }),
  );
  assert.ok(bad);
  assert.equal(bad.autoPrice, null);
  assert.equal(bad.taobaoSnapshot, null);
});
