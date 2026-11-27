import assert from "node:assert/strict";
import test from "node:test";
import { intakeToPrefill, prefillToDraft, sanitizeIntakeSubmission, type IntakeSubmission } from "../lib/intake-import";

/**
 * Cross-app color contract. The intake form stores `color` as the chip list
 * joined with ", " (sassy-closet/components/IntakeApp.tsx `colorLine`), and a
 * piece carries the same joined text. The shop shows one chip, one photo tag,
 * and one JSON colour per stored colour, so a joined string must become one
 * colour per chip — otherwise the draft ships a single bogus colour.
 *
 * Fixture colours and fake mãs only. No catalog, price, or seed row changes.
 */

function submission(over: Partial<Record<string, unknown>> = {}): IntakeSubmission {
  const parsed = sanitizeIntakeSubmission({
    id: 1,
    ma: "A30",
    kind: "A",
    size: "S",
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

function names(color: string, pieces: unknown[] = []): string[] {
  return intakeToPrefill(submission({ color, pieces })).colors.map((entry) => entry.name);
}

test("a joined intake color line becomes one colour per chip", () => {
  assert.deepEqual(names("Đen"), ["Đen"]);
  assert.deepEqual(names("Đen, Trắng"), ["Đen", "Trắng"]);
  assert.deepEqual(names("Đen, Kem, Xanh"), ["Đen", "Kem", "Xanh"]);
});

test("a chip line with no space after the comma still splits", () => {
  assert.deepEqual(names("Đen,Trắng"), ["Đen", "Trắng"]);
  assert.deepEqual(names("Đen ,Kem"), ["Đen", "Kem"]);
});

test("a colour name that contains a space stays one colour", () => {
  // "Xanh dương" and "Hồng đậm" are single intake chips; only a comma separates.
  assert.deepEqual(names("Xanh dương"), ["Xanh dương"]);
  assert.deepEqual(names("Xanh dương, Hồng đậm"), ["Xanh dương", "Hồng đậm"]);
  assert.deepEqual(names("Trắng ngà, Đỏ đô"), ["Trắng ngà", "Đỏ đô"]);
});

test("repeated chips collapse instead of showing the same colour twice", () => {
  assert.deepEqual(names("Đen, đen, ĐEN, Trắng"), ["Đen", "Trắng"]);
  assert.deepEqual(names("Kem, Kem"), ["Kem"]);
});

test("blank and trailing separators never invent a colour", () => {
  assert.deepEqual(names(""), []);
  assert.deepEqual(names("   "), []);
  assert.deepEqual(names("Đen,"), ["Đen"]);
  assert.deepEqual(names("Đen, , Trắng"), ["Đen", "Trắng"]);
  assert.deepEqual(names(", ,"), []);
});

test("a piece colour line splits the same way and stays a confirmed colour", () => {
  const prefill = intakeToPrefill(
    submission({ pieces: [{ id: "p1", photos: [], suggested: [], color: "Đen, Trắng", note: "" }] }),
  );
  assert.deepEqual(prefill.colors.map((entry) => entry.name), ["Đen", "Trắng"]);
  assert.deepEqual(prefill.colors.map((entry) => entry.truth), ["confirmed", "confirmed"]);
});

test("a colour confirmed on the row is not downgraded by a piece suggestion", () => {
  const prefill = intakeToPrefill(
    submission({
      color: "Đen, Trắng",
      pieces: [{ id: "p1", photos: [], suggested: ["Đen", "Kem"], color: "", note: "" }],
    }),
  );
  const byName = new Map(prefill.colors.map((entry) => [entry.name, entry.truth]));
  assert.equal(byName.get("Đen"), "confirmed");
  assert.equal(byName.get("Trắng"), "confirmed");
  assert.equal(byName.get("Kem"), "unconfirmed");
});

test("the draft built from a joined color line carries every colour", () => {
  const draft = prefillToDraft(intakeToPrefill(submission({ color: "Đen, Trắng, Kem" })));
  assert.deepEqual(draft.colors.map((color) => color.name), ["Đen", "Trắng", "Kem"]);
  // Ids stay unique so each chip can take its own swatch and photos.
  assert.equal(new Set(draft.colors.map((color) => color.id)).size, 3);
});

test("the intake form's own join is the shape this reads", () => {
  // Mirror of IntakeApp `colorLine`: [...colors, ...sellerColors].join(", ").
  const chips = ["Đen", "Xanh dương", "Hồng đậm"];
  const stored = chips.join(", ");
  assert.equal(stored, "Đen, Xanh dương, Hồng đậm");
  assert.deepEqual(names(stored), chips);
});
