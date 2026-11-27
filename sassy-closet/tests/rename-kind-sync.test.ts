import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { exportCsv, getSubmission, saveSubmission, type SaveInput } from "../lib/store";

/**
 * The mã letter says the kind: A01 is an Áo, G02 is Giày. resolveSaveMa takes
 * only the number from a typed new mã and keeps input.kind, so renaming across
 * letters stored P01 with kind A. The caption then read "Chiếc áo", the find
 * card showed "Áo", and the CSV wrote kind A / kind_vi Áo for a P mã — wrong
 * clothing copy and the wrong size scale (P uses 2XS–2XL, G uses 35–41).
 */
describe("renaming across letters keeps kind and mã in step", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-rename-kind-"));
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

  test("a full mã of another letter moves the row to that kind", async () => {
    const created = await saveSubmission(blankSave({ kind: "A", size: "M", color: "Đen" }));
    assert.equal(created.ma, "A01");
    assert.equal(created.kind, "A");

    const renamed = await saveSubmission(
      blankSave({ kind: "A", size: "M", color: "Đen", existingMa: created.ma, newMa: "P01" }),
    );
    assert.equal(renamed.ma, "P01");
    assert.equal(renamed.kind, "P");
    assert.match(renamed.caption_vi, /Món nhỏ xinh xỉu/);
    assert.doesNotMatch(renamed.caption_vi, /Chiếc áo/);

    const stored = await getSubmission("P01");
    assert.ok(stored);
    assert.equal(stored.kind, "P");
    const csv = await exportCsv();
    assert.match(csv, /^P01,P,Phụ kiện,/m);
  });

  test("a bare letter keeps the form kind: renaming to P mints P01 with kind P", async () => {
    const created = await saveSubmission(blankSave({ kind: "A", size: "M" }));
    const renamed = await saveSubmission(blankSave({ kind: "P", existingMa: created.ma, newMa: "P" }));
    assert.equal(renamed.ma, "P01");
    assert.equal(renamed.kind, "P");
    assert.match(renamed.caption_vi, /Món nhỏ xinh xỉu/);
  });

  test("a same-letter rename and a plain edit leave kind alone", async () => {
    const created = await saveSubmission(blankSave({ kind: "A", size: "M", color: "Đỏ" }));
    const sameLetter = await saveSubmission(
      blankSave({ kind: "A", color: "Đỏ", existingMa: created.ma, newMa: "A05" }),
    );
    assert.equal(sameLetter.ma, "A05");
    assert.equal(sameLetter.kind, "A");

    const edited = await saveSubmission(blankSave({ kind: "A", color: "Kem", existingMa: "A05" }));
    assert.equal(edited.ma, "A05");
    assert.equal(edited.kind, "A");
    assert.match(edited.caption_vi, /Chiếc áo/);
  });

  test("a G mã takes the shoe size scale in the caption and the CSV", async () => {
    const created = await saveSubmission(
      blankSave({ kind: "A", size: "38", color: "Đen", newMa: "G02" }),
    );
    assert.equal(created.ma, "G02");
    assert.equal(created.kind, "G");
    const csv = await exportCsv();
    assert.match(csv, /^G02,G,Giày \/ Cao gót,/m);
    assert.match(csv, /35 36 37 38 39 40 41/);
  });
});

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
