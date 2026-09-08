import assert from "node:assert/strict";
import { test } from "node:test";
import { buildMaLookup } from "../lib/ma-card";
import {
  STAGED_ONLY_MESSAGE,
  dashIfEmpty,
  moneyLine,
  normalizeFindCode,
  photoFolder,
  sanitizeOnHandRows,
} from "../lib/on-hand";
import type { Submission } from "../lib/types";

function stagedItem(overrides: Partial<Submission> = {}): Submission {
  return {
    id: 1,
    ma: "A01",
    kind: "A",
    size: "M L",
    color: "Kem, Xanh",
    color_note: "pastel nhẹ",
    pieces: [],
    link: "https://e.tb.cn/example",
    price: "28",
    cost_cny: "80",
    cost_usd: "12",
    cost_currency: "USD",
    sell_cny: "",
    sell_usd: "28",
    sell_currency: "USD",
    blurb: "",
    photo_paths: ["A01/001.jpg"],
    photo_hashes: ["abc"],
    status: "staged",
    square: "not_square",
    created_at: "2026-09-08T00:00:00.000Z",
    updated_at: "2026-09-08T00:00:00.000Z",
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: "Documents/Sassy Closet/Photos/A01/",
    ...overrides,
  };
}

test("normalize find code trims and uppers without inventing a new mã", () => {
  assert.equal(normalizeFindCode("  a01  "), "A01");
  assert.equal(normalizeFindCode("p05"), "P05");
  assert.equal(normalizeFindCode(""), "");
});

test("missing cost/sell/notes display as dash — never invent $", () => {
  assert.equal(dashIfEmpty(""), "—");
  assert.equal(dashIfEmpty(null), "—");
  assert.equal(moneyLine("", ""), "—");
  assert.equal(moneyLine("12", ""), "$12");
  assert.equal(moneyLine("", "80"), "¥80");
});

test("buildMaLookup does not invent on-hand rows from staged sizes or colors", () => {
  const card = buildMaLookup(stagedItem(), []);
  assert.equal(card.code, "A01");
  assert.equal(card.staged.kind_label, "Áo");
  assert.equal(card.staged.colors, "Kem, Xanh");
  assert.equal(card.staged.sizes, "M L");
  assert.equal(card.staged.source_link, "https://e.tb.cn/example");
  assert.deepEqual(card.on_hand, []);
  assert.equal(card.staged_only, true);
  assert.equal(card.on_hand.length, 0);
});

test("sanitizeOnHandRows keeps explicit qty 0 and never invents missing qty or status", () => {
  const rows = sanitizeOnHandRows(
    [
      { size: "M", color: "Kem", qty_on_hand: 0, status: "sold" },
      { size: "L", color: "Xanh", status: "Available" },
      { size: "S", color: "Đen", qty_on_hand: 2, status: "on_hand", storage_location: "bin A" },
      "skip-me",
    ],
    "A01",
  );
  assert.equal(rows.length, 3);
  assert.equal(rows[0].qty_on_hand, 0);
  assert.equal(rows[0].status, "sold");
  assert.equal(rows[1].qty_on_hand, null);
  assert.equal(rows[1].status, "");
  assert.equal(rows[2].qty_on_hand, 2);
  assert.equal(rows[2].status, "on_hand");
  assert.equal(rows[2].storage_location, "bin A");
  assert.equal(rows[2].where_stored, "Documents/Sassy Closet/Photos/A01/");
});

test("non-array on-hand data stays empty — no fake Square Free counts", () => {
  assert.deepEqual(sanitizeOnHandRows(undefined, "A01"), []);
  assert.deepEqual(sanitizeOnHandRows({ qty: 99 }, "A01"), []);
  assert.equal(STAGED_ONLY_MESSAGE, "Staged only — not on Square On_Hand yet");
  assert.equal(photoFolder("a01"), "Documents/Sassy Closet/Photos/A01/");
});

test("card passes through real on-hand rows when the store actually has them", () => {
  const onHand = sanitizeOnHandRows(
    [{ size: "M", color: "Kem", qty_on_hand: 1, status: "reserved" }],
    "A01",
  );
  const card = buildMaLookup(stagedItem(), onHand);
  assert.equal(card.staged_only, false);
  assert.equal(card.on_hand.length, 1);
  assert.equal(card.on_hand[0].qty_on_hand, 1);
  assert.equal(card.on_hand[0].status, "reserved");
});
