import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { getSubmission, saveSubmission, type SaveInput } from "../lib/store";

/**
 * "Sửa theo mã" sends only the fields its form renders. The blurb, English
 * caption, and suggested blurb have no input on that form, so saveSubmission
 * rebuilt them from "" and an edit wiped copy that was already on the row.
 * D05's real title lives in blurb (lib/intake-d05-seed.ts), so the shop import
 * lost it too.
 */
describe("editing a mã keeps the copy the form does not show", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-edit-copy-"));
    for (const key of [
      "SASSY_DATA_DIR",
      "VERCEL",
      "BLOB_READ_WRITE_TOKEN",
      "BLOB_STORE_ID",
      "BLOB_ACCESS",
      "INTAKE_DATASET_SYNC_WEBHOOK_URL",
      "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
    ]) {
      prev[key] = process.env[key];
      delete process.env[key];
    }
    process.env.SASSY_DATA_DIR = tmp;
    resetStoreBackendForTests();
  });

  afterEach(() => {
    for (const [key, value] of Object.entries(prev)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("an edit keeps blurb, caption_en, and blurb_suggested", async () => {
    const created = await saveSubmission(blankSave({ color: "Đen", size: "M" }));
    assert.equal(created.ma, "A01");
    await seedCopy(created.ma, {
      blurb: "Đầm ren nhún apricot",
      caption_en: "A01 apricot lace dress",
      blurb_suggested: "Đầm ren",
    });

    await saveSubmission(blankSave({ color: "Kem", size: "L", existingMa: created.ma }));

    const edited = await getSubmission(created.ma);
    assert.ok(edited);
    assert.equal(edited.color, "Kem");
    assert.equal(edited.size, "L");
    assert.equal(edited.blurb, "Đầm ren nhún apricot");
    assert.equal(edited.caption_en, "A01 apricot lace dress");
    assert.equal(edited.blurb_suggested, "Đầm ren");
  });

  test("a row with no stored copy still saves with empty copy, and no key invented", async () => {
    const created = await saveSubmission(blankSave({ color: "Trắng" }));
    await saveSubmission(blankSave({ color: "Be", existingMa: created.ma }));
    const edited = await getSubmission(created.ma);
    assert.ok(edited);
    assert.equal(edited.blurb, "");
    assert.equal(edited.caption_en, "");
    assert.equal(edited.blurb_suggested, "");
  });

  test("a new row starts with empty copy rather than inheriting another mã", async () => {
    const first = await saveSubmission(blankSave({ kind: "A", color: "Đỏ" }));
    await seedCopy(first.ma, { blurb: "Chiếc áo đỏ", caption_en: "A01 red top", blurb_suggested: "áo đỏ" });

    const second = await saveSubmission(blankSave({ kind: "A", color: "Xanh" }));
    assert.equal(second.ma, "A02");
    assert.equal(second.blurb, "");
    assert.equal(second.caption_en, "");
    assert.equal(second.blurb_suggested, "");
  });
});

/** Write the copy straight into the store file: no intake form field sets it. */
async function seedCopy(ma: string, copy: { blurb: string; caption_en: string; blurb_suggested: string }) {
  const file = path.join(process.env.SASSY_DATA_DIR ?? "", "submissions.json");
  const store = JSON.parse(fs.readFileSync(file, "utf8")) as {
    submissions: { ma: string; blurb: string; caption_en: string; blurb_suggested: string }[];
  };
  const row = store.submissions.find((item) => item.ma === ma);
  assert.ok(row, `stored row ${ma}`);
  row.blurb = copy.blurb;
  row.caption_en = copy.caption_en;
  row.blurb_suggested = copy.blurb_suggested;
  fs.writeFileSync(file, JSON.stringify(store, null, 2));
}

function blankSave(overrides: Partial<SaveInput> = {}): SaveInput {
  return {
    kind: "A",
    size: "",
    link: "",
    color: "",
    color_note: "",
    pieces: [],
    cost_usd: "",
    cost_cny: "",
    cost_currency: "USD",
    sell_usd: "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: [],
    photos: [],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    ...overrides,
  };
}
