import assert from "node:assert/strict";
import test from "node:test";
import { EU_SHOE_SIZES, isShopSize } from "../lib/asia-size";
import {
  intakeToPrefill,
  prefillToDraft,
  sanitizeIntakeSubmission,
  type IntakeSubmission,
} from "../lib/intake-import";
import { validateItemDraft } from "../lib/item-draft";

/**
 * Intake stores `size` as the chip list joined with a space
 * (sassy-closet/components/IntakeApp.tsx `form.set("size", sizes.join(" "))`).
 * For a giày look the chips come from `sizesForKind("G")`, which is the EU
 * range 35–41, so a G submission stores "37 38".
 *
 * The importer only accepted Asia letters, so every EU size on a shoe look was
 * reported as "Dropped unknown size tokens" and the draft reached /admin/new
 * with an empty size list. EU shoe sizes are a stored shop size
 * (`isShopSize`, `EU_SHOE_SIZES`), so the chip is real and must survive.
 *
 * Fake mãs only. No catalog, price, seed, or held.json change.
 */

function submission(over: Partial<Record<string, unknown>> = {}): IntakeSubmission {
  const parsed = sanitizeIntakeSubmission({
    id: 1,
    ma: "G03",
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
    ...over,
  });
  assert.ok(parsed);
  return parsed;
}

function prefillSizes(size: string): { sizes: string[]; dropped: string[]; warnings: string[] } {
  const prefill = intakeToPrefill(submission({ size }));
  return { sizes: prefill.sizes, dropped: prefill.droppedSizes, warnings: prefill.warnings };
}

test("every EU shoe size the intake shoe kind offers is a stored shop size", () => {
  assert.deepEqual([...EU_SHOE_SIZES], ["34", "35", "36", "37", "38", "39", "40", "41", "42"]);
  for (const size of EU_SHOE_SIZES) {
    assert.equal(isShopSize(size), true, `${size} is an EU shoe size`);
  }
});

test("a shoe submission keeps each EU size chip instead of dropping it", () => {
  const { sizes, dropped } = prefillSizes("37 38");
  assert.deepEqual(sizes, ["37", "38"]);
  assert.deepEqual(dropped, [], "an EU shoe size is not an unknown token");

  const single = prefillSizes("40");
  assert.deepEqual(single.sizes, ["40"]);
  assert.deepEqual(single.dropped, []);

  const range = EU_SHOE_SIZES.filter((size) => size >= "35" && size <= "41");
  assert.deepEqual(prefillSizes(range.join(" ")).sizes, [...range]);
});

test("the shoe draft reaches Add with the stored sizes and still validates", () => {
  const prefill = intakeToPrefill(submission({ size: "37 38" }));
  const draft = prefillToDraft(prefill);
  assert.deepEqual(draft.sizes, ["37", "38"]);
  assert.equal(draft.status, "hold", "an imported draft is staged, never available");
  // The only remaining blocker is the title an importer leaves blank on purpose.
  assert.equal(validateItemDraft({ ...draft, titleEn: "Shoes" }), null);
});

test("Asia letters keep working, and duplicates collapse", () => {
  assert.deepEqual(prefillSizes("S M L").sizes, ["S", "M", "L"]);
  assert.deepEqual(prefillSizes("37 37").sizes, ["37"]);
  assert.deepEqual(prefillSizes("S 37").sizes, ["S", "37"]);
});

test("a token that is neither Asia nor EU is still dropped and reported", () => {
  const { sizes, dropped, warnings } = prefillSizes("S 12 均码");
  assert.deepEqual(sizes, ["S"]);
  assert.deepEqual(dropped, ["12", "均码"]);
  assert.match(warnings.join("\n"), /Dropped unknown size tokens/);
});
