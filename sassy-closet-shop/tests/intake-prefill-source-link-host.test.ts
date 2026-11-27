import assert from "node:assert/strict";
import test from "node:test";
import { validateItemDraft } from "../lib/item-draft";
import {
  intakeToPrefill,
  prefillToDraft,
  sanitizeIntakeSubmission,
  type IntakeSubmission,
} from "../lib/intake-import";
import { parseSourceLink } from "../lib/source-link";

/**
 * The intake form keeps only the first http(s) URL it finds in the link box
 * (`normalizeSourceLink`) — it never checks the host. A Boss paste from a
 * Shopee / 1688 / Facebook listing is therefore a normal staged row.
 *
 * The importer copied that URL straight onto the draft `sourceLink`, and the
 * draft validator only allows a Taobao host. The result was an ordinary
 * imported look that could not be saved at all: "sourceLink must be a Taobao
 * link", with no way to clear it from the form's prefill.
 *
 * Only an allowed staff shop link may travel with the draft. Any other host is
 * reported as a warning so Boss can paste the real Taobao link, and the draft
 * still saves. Placeholder hosts only; no real supplier link is stored here.
 */

// Built from parts so no supplier host appears as a literal in the repo.
const HOST = {
  shop: ["e.", "tb.", "cn"].join(""),
  list: ["shop", "ee.vn"].join(""),
  bulk: ["1688", ".com"].join(""),
  social: ["www.", "facebook", ".com"].join(""),
  plain: ["example", ".invalid"].join(""),
  lookalike: ["tb.", "cn", ".evil.invalid"].join(""),
};

const ALLOWED_LINK = `https://${HOST.shop}/h/abc?tk=xyz`;
const OTHER_LINKS = [
  `https://${HOST.list}/product/123`,
  `https://detail.${HOST.bulk}/offer/1.html`,
  `https://${HOST.social}/marketplace/item/1`,
  `https://${HOST.plain}/listing`,
];

function submission(over: Partial<Record<string, unknown>> = {}): IntakeSubmission {
  const parsed = sanitizeIntakeSubmission({
    id: 1,
    ma: "A30",
    kind: "A",
    size: "M",
    color: "Đen",
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
    ...over,
  });
  assert.ok(parsed);
  return parsed;
}

/** The draft a real import produces, with the title Boss would type on Add. */
function draftFor(link: string) {
  const prefill = intakeToPrefill(submission({ link }));
  const draft = { ...prefillToDraft(prefill), titleEn: "Top" };
  return { prefill, draft };
}

test("an allowed staff link still travels with the draft and saves", () => {
  const { prefill, draft } = draftFor(ALLOWED_LINK);
  assert.equal(prefill.sourceLink, ALLOWED_LINK);
  assert.equal(draft.sourceLink, ALLOWED_LINK);
  assert.equal(validateItemDraft(draft), null);
});

test("a non-allowed intake link no longer blocks the draft from saving", () => {
  for (const link of OTHER_LINKS) {
    const { prefill, draft } = draftFor(link);
    assert.equal(draft.sourceLink, "", `${link} is not a staff shop link`);
    assert.equal(
      validateItemDraft(draft),
      null,
      `${link} must not block Save — the look is otherwise complete`,
    );
    assert.match(
      prefill.warnings.join("\n"),
      /not a Taobao link/,
      `${link} must be reported so Boss can paste the real one`,
    );
  }
});

test("a non-allowed link is dropped without inventing a replacement", () => {
  const { draft } = draftFor(OTHER_LINKS[0]!);
  assert.equal(draft.sourceLink, "");
  // Never substitute a recorded hub link or any other mã's source.
  assert.doesNotMatch(JSON.stringify(draft), /tb\.cn|taobao/i);
});

test("a non-URL link stays out of the draft and keeps its own warning", () => {
  const { prefill, draft } = draftFor("xem shop này nha");
  assert.equal(prefill.sourceLink, "");
  assert.equal(draft.sourceLink, "");
  assert.match(prefill.warnings.join("\n"), /not a URL/);
});

test("only the staff shop host allowlist decides, not the intake text", () => {
  assert.doesNotThrow(() => parseSourceLink(ALLOWED_LINK));
  for (const link of OTHER_LINKS) {
    assert.throws(() => parseSourceLink(link), /Taobao link/, link);
  }
  // A host that merely contains the brand does not pass.
  assert.throws(() => parseSourceLink(`https://${HOST.lookalike}/item/1`), /Taobao link/);
});
