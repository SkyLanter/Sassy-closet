import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { canSaveEdit, editSaveIntent, renameAfterKindChange } from "../lib/edit-form";
import { photosRoot } from "../lib/paths";
import { saveSubmission } from "../lib/store";
import type { SaveInput } from "../lib/store";

type StoreCache = typeof globalThis & { __sassyStore?: unknown };

function resetIsolatedStore(): void {
  process.env.SASSY_DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-store-"));
  delete (globalThis as StoreCache).__sassyStore;
}

function sampleSave(overrides: Partial<SaveInput> = {}): SaveInput {
  return {
    kind: "A",
    size: "M",
    link: "",
    color: "Kem",
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
    newMa: "A01",
    ...overrides,
  };
}

beforeEach(() => {
  resetIsolatedStore();
});

afterEach(() => {
  delete process.env.SASSY_DATA_DIR;
  delete (globalThis as StoreCache).__sassyStore;
});

test("Lưu on Sửa stays disabled until a mã is actually loaded", () => {
  assert.equal(canSaveEdit(null), false);
  assert.equal(canSaveEdit(""), false);
  assert.equal(canSaveEdit("A01"), true);
  assert.equal(editSaveIntent(null, "Q01"), null);
  assert.deepEqual(editSaveIntent("A01", "  Q01  "), { ma: "A01", renameTo: "Q01" });
  assert.deepEqual(editSaveIntent("A01", "   "), { ma: "A01", renameTo: null });
});

test("kind toggle clears rename when switching back to the loaded type", () => {
  assert.equal(renameAfterKindChange("A01", "Q", ["A01"]), "Q01");
  assert.equal(renameAfterKindChange("A01", "A", ["A01"]), "");
  assert.equal(renameAfterKindChange(null, "Q", []), "");
});

test("rename moves kept photos onto the new mã folder", () => {
  const bytes = Buffer.from("sassy-photo");
  const created = saveSubmission(
    sampleSave({
      photos: [{ bytes, hash: "hash-a01", ext: ".jpg" }],
    }),
  );
  assert.equal(created.ma, "A01");
  assert.deepEqual(created.photo_paths, ["A01/001.jpg"]);
  const oldFile = path.join(photosRoot(), "A01", "001.jpg");
  assert.equal(fs.existsSync(oldFile), true);

  const renamed = saveSubmission(
    sampleSave({
      kind: "Q",
      existingMa: "A01",
      newMa: "Q01",
      keep_photos: ["A01/001.jpg"],
      photos: [],
    }),
  );
  assert.equal(renamed.ma, "Q01");
  assert.deepEqual(renamed.photo_paths, ["Q01/001.jpg"]);
  assert.match(renamed.photo_link, /Photos\/Q01\/$/);
  assert.deepEqual(renamed.photo_hashes, ["hash-a01"]);
  assert.equal(fs.existsSync(path.join(photosRoot(), "Q01", "001.jpg")), true);
  assert.equal(fs.existsSync(oldFile), false);
});
