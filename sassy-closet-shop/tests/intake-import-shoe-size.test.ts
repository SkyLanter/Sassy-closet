import assert from "node:assert/strict";
import test from "node:test";
import { intakeToPrefill, type IntakeSubmission } from "../lib/intake-import";

function submission(kind: string, ma: string, size: string): IntakeSubmission {
  return {
    id: 0,
    ma,
    kind,
    size,
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
    square: "",
    created_at: "",
    updated_at: "",
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: "",
  };
}

test("a G import keeps EU sizes and a single trailing .0", () => {
  const shoe = intakeToPrefill(submission("G", "G01", "40.0 35,36"));
  assert.deepEqual(shoe.sizes, ["40", "35", "36"]);
  assert.deepEqual(shoe.droppedSizes, []);
  const edge = intakeToPrefill(submission("G", "G01", "33.0 43 34.5 40.00 42"));
  assert.deepEqual(edge.sizes, ["42"]);
  assert.deepEqual(edge.droppedSizes, ["33.0", "43", "34.5", "40.00"]);
});

test("clothing and kind O imports stay on letters", () => {
  const clothing = intakeToPrefill(submission("A", "A01", "S XXS 40"));
  assert.deepEqual(clothing.sizes, ["S"]);
  assert.deepEqual(clothing.droppedSizes, ["XXS", "40"]);
  const boots = intakeToPrefill(submission("O", "O01", "36 M"));
  assert.deepEqual(boots.sizes, ["M"]);
  assert.deepEqual(boots.droppedSizes, ["36"]);
});
