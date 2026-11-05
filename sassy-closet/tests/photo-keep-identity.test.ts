import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { findByPhotoHash, hashBytes, readPhoto, saveSubmission } from "../lib/store";
import type { SaveInput } from "../lib/store";
import type { Submission } from "../lib/types";

function blank(overrides: Partial<SaveInput> = {}): SaveInput {
  return {
    kind: "A",
    size: "",
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
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    ...overrides,
  };
}

function shot(text: string, ext: string) {
  const bytes = Buffer.from(text);
  return { bytes, hash: hashBytes(bytes), ext };
}

describe("a kept path keeps that photo's hash", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-photo-keep-id-"));
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

  test("a short path list does not inherit a removed photo hash", async () => {
    const real = shot("real-003-bytes", ".jpg");
    const created = await saveSubmission(blank({ photos: [real] }));
    assert.deepEqual(created.photo_paths, ["A01/001.jpg"]);

    const src = path.join(tmp, "photos", "A01", "001.jpg");
    const dest = path.join(tmp, "photos", "A01", "003.jpg");
    fs.copyFileSync(src, dest);
    fs.rmSync(src);

    const file = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: Submission[];
    };
    const row = store.submissions[0];
    assert.ok(row);
    row.photo_paths = ["A01/003.jpg"];
    row.photo_hashes = ["removed-hash-001", "removed-hash-002", real.hash];
    fs.writeFileSync(file, JSON.stringify(store));
    resetStoreBackendForTests();

    const updated = await saveSubmission(
      blank({ existingMa: "A01", keep_photos: ["A01/003.jpg"] }),
    );
    assert.deepEqual(updated.photo_paths, ["A01/003.jpg"]);
    assert.deepEqual(updated.photo_hashes, [real.hash]);
    assert.equal((await findByPhotoHash("removed-hash-001")).length, 0);
    assert.equal((await findByPhotoHash("removed-hash-002")).length, 0);
    const hits = await findByPhotoHash(real.hash);
    assert.equal(hits.length, 1);
    assert.equal(hits[0]?.ma, "A01");
  });

  test("a short path list with a missing file does not keep the removed hash", async () => {
    const orphan = shot("never-copied-to-003", ".jpg");
    await saveSubmission(blank({ photos: [orphan] }));
    fs.rmSync(path.join(tmp, "photos", "A01", "001.jpg"));

    const file = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: Submission[];
    };
    const row = store.submissions[0];
    assert.ok(row);
    row.photo_paths = ["A01/003.jpg"];
    row.photo_hashes = ["removed-hash", "other"];
    fs.writeFileSync(file, JSON.stringify(store));
    resetStoreBackendForTests();
    assert.equal(fs.existsSync(path.join(tmp, "photos", "A01", "003.jpg")), false);

    const updated = await saveSubmission(
      blank({ existingMa: "A01", keep_photos: ["A01/003.jpg"] }),
    );
    assert.deepEqual(updated.photo_hashes, [""]);
    assert.equal((await findByPhotoHash("removed-hash")).length, 0);
    assert.equal((await findByPhotoHash("other")).length, 0);
  });

  test("an alias keep path keeps the hash when the row is renamed", async () => {
    const original = shot("rename-alias-bytes", ".jpg");
    await saveSubmission(blank({ photos: [original] }));
    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["/A01/001.jpg"],
      }),
    );
    assert.deepEqual(renamed.photo_paths, ["A09/001.jpg"]);
    assert.deepEqual(renamed.photo_hashes, [original.hash]);
    assert.notEqual(renamed.photo_hashes[0], "");
    const kept = await findByPhotoHash(original.hash);
    assert.equal(kept.length, 1);
    assert.equal(kept[0]?.ma, "A09");

    const second = shot("second-row-bytes", ".jpg");
    const minted = await saveSubmission(blank({ photos: [second] }));
    const ma = minted.ma;
    const moved = await saveSubmission(
      blank({
        existingMa: ma,
        newMa: "A11",
        keep_photos: [`${ma}/./001.jpg`],
      }),
    );
    assert.deepEqual(moved.photo_hashes, [second.hash]);
    assert.notEqual(moved.photo_hashes[0], "");
    assert.equal((await readPhoto("A11/001.jpg"))?.bytes.toString(), "second-row-bytes");
    const found = await findByPhotoHash(second.hash);
    assert.equal(found.length, 1);
    assert.equal(found[0]?.ma, "A11");
  });

  test("a different folder case keeps the hash and does not overwrite the file", async () => {
    const original = shot("original-bytes", ".jpg");
    const added = shot("new-bytes", ".jpg");
    await saveSubmission(blank({ photos: [original] }));
    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["a01/001.jpg"],
        photos: [added],
      }),
    );
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "original-bytes");
    assert.equal((await readPhoto("A01/002.jpg"))?.bytes.toString(), "new-bytes");
    const keepIndex = updated.photo_paths.indexOf("a01/001.jpg");
    assert.notEqual(keepIndex, -1);
    assert.equal(updated.photo_hashes[keepIndex], original.hash);
    const originalHits = await findByPhotoHash(original.hash);
    assert.equal(originalHits.length, 1);
    assert.equal(originalHits[0]?.ma, "A01");
    const addedHits = await findByPhotoHash(added.hash);
    assert.equal(addedHits.length, 1);
    assert.equal(addedHits[0]?.ma, "A01");
  });

  test("a different folder and extension case does not overwrite slot 001", async () => {
    const original = shot("original-bytes", ".jpg");
    const added = shot("new-bytes", ".jpg");
    await saveSubmission(blank({ photos: [original] }));
    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["a01/001.JPG"],
        photos: [added],
      }),
    );
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "original-bytes");
    assert.notEqual((await readPhoto("A01/001.jpg"))?.bytes.toString(), "new-bytes");
    assert.equal((await readPhoto("A01/002.jpg"))?.bytes.toString(), "new-bytes");
    const keepIndex = updated.photo_paths.indexOf("a01/001.JPG");
    assert.notEqual(keepIndex, -1);
    assert.equal(updated.photo_hashes[keepIndex], "");
    assert.equal((await findByPhotoHash(original.hash)).length, 0);
    assert.equal((await findByPhotoHash(added.hash))[0]?.ma, "A01");
  });

  test("the exact keep spelling wins when the same photo key has two hashes", async () => {
    const real = shot("lowercase-file-bytes", ".jpg");
    const created = await saveSubmission(blank({ photos: [real] }));
    const file = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: Submission[];
    };
    const row = store.submissions[0];
    assert.ok(row);
    row.photo_paths = ["A01/001.jpg", "a01/001.jpg"];
    row.photo_hashes = ["removed-hash", real.hash];
    fs.writeFileSync(file, JSON.stringify(store));
    resetStoreBackendForTests();

    const updated = await saveSubmission(
      blank({ existingMa: created.ma, keep_photos: ["a01/001.jpg"] }),
    );
    assert.deepEqual(updated.photo_hashes, [real.hash]);
    assert.equal((await findByPhotoHash("removed-hash")).length, 0);
    const hits = await findByPhotoHash(real.hash);
    assert.equal(hits.length, 1);
    assert.equal(hits[0]?.ma, "A01");
  });

  test("a mismatched hash list does not take another mã's file", async () => {
    const original = shot("a01-bytes", ".jpg");
    await saveSubmission(blank({ photos: [original] }));
    const other = shot("a02-bytes", ".jpg");
    const second = await saveSubmission(blank({ photos: [other] }));
    const file = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: Submission[];
    };
    const row = store.submissions.find((item) => item.ma === second.ma);
    assert.ok(row);
    row.photo_hashes = ["stale-hash", "extra-hash"];
    fs.writeFileSync(file, JSON.stringify(store));
    resetStoreBackendForTests();

    const updated = await saveSubmission(
      blank({ existingMa: second.ma, keep_photos: ["A01/001.jpg"] }),
    );
    assert.deepEqual(updated.photo_hashes, [""]);
    const hits = await findByPhotoHash(original.hash);
    assert.equal(hits.length, 1);
    assert.equal(hits[0]?.ma, "A01");
    assert.equal((await findByPhotoHash("stale-hash")).length, 0);
  });

  test("a folder path on a mismatched hash list does not fail the save", async () => {
    const original = shot("dir-keep-bytes", ".jpg");
    const created = await saveSubmission(blank({ photos: [original] }));
    const file = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: Submission[];
    };
    const row = store.submissions[0];
    assert.ok(row);
    row.photo_hashes = ["stale-hash", "extra-hash"];
    fs.writeFileSync(file, JSON.stringify(store));
    resetStoreBackendForTests();

    const updated = await saveSubmission(
      blank({ existingMa: created.ma, keep_photos: ["A01"] }),
    );
    assert.deepEqual(updated.photo_hashes, [""]);
    assert.equal((await findByPhotoHash("stale-hash")).length, 0);
    assert.equal((await findByPhotoHash(original.hash)).length, 0);
  });
});
