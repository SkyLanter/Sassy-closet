import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { findByPhotoHash, hashBytes, readPhoto, saveSubmission, type SaveInput } from "../lib/store";

/**
 * "Sửa theo mã" sends keep_photos for the files it still wants and appends
 * any new upload. Numbering the new file from the kept count, and copying
 * every old hash, overwrites a kept photo when the names are not 1..n and
 * leaves the dropped photo findable.
 */
describe("editing photos keeps the files that were kept", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-photo-keep-"));
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

  test("dropping a middle photo and adding one does not overwrite a kept file", async () => {
    const first = Buffer.from("photo-001");
    const middle = Buffer.from("photo-002-dropped");
    const third = Buffer.from("photo-003-kept");
    const added = Buffer.from("photo-004-new");
    const created = await saveSubmission(
      input({
        photos: [shot(first), shot(middle), shot(third)],
      }),
    );
    assert.deepEqual(created.photo_paths, ["A01/001.jpg", "A01/002.jpg", "A01/003.jpg"]);

    const edited = await saveSubmission(
      input({
        existingMa: created.ma,
        keep_photos: ["A01/001.jpg", "A01/003.jpg"],
        photos: [shot(added)],
        color: "Kem",
      }),
    );

    assert.deepEqual(edited.photo_paths, ["A01/001.jpg", "A01/003.jpg", "A01/004.jpg"]);
    assert.equal(edited.photo_hashes.length, edited.photo_paths.length);
    assert.equal(edited.photo_hashes.includes(hashBytes(middle)), false);
    assert.deepEqual(edited.photo_hashes, [hashBytes(first), hashBytes(third), hashBytes(added)]);

    const keptThird = await readPhoto("A01/003.jpg");
    assert.equal(keptThird?.bytes.toString(), "photo-003-kept");
    const createdFile = await readPhoto("A01/004.jpg");
    assert.equal(createdFile?.bytes.toString(), "photo-004-new");
    assert.equal((await findByPhotoHash(hashBytes(middle))).length, 0);
    assert.equal((await findByPhotoHash(hashBytes(third)))[0]?.ma, "A01");
  });

  test("a contiguous add still uses the next number", async () => {
    const created = await saveSubmission(input({ photos: [shot(Buffer.from("one")), shot(Buffer.from("two"))] }));
    const edited = await saveSubmission(
      input({
        existingMa: created.ma,
        keep_photos: created.photo_paths,
        photos: [shot(Buffer.from("three"))],
      }),
    );
    assert.deepEqual(edited.photo_paths, ["A01/001.jpg", "A01/002.jpg", "A01/003.jpg"]);
    assert.equal(edited.photo_hashes.length, 3);
  });
});

function shot(bytes: Buffer): SaveInput["photos"][number] {
  return { bytes, hash: hashBytes(bytes), ext: ".jpg" };
}

function input(overrides: Partial<SaveInput> = {}): SaveInput {
  return {
    kind: "A",
    size: "M",
    link: "",
    color: "Đen",
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
