import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { hashBytes, readPhoto, saveSubmission } from "../lib/store";
import type { SaveInput } from "../lib/store";

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

describe("new photos do not replace a kept file", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-photo-gap-"));
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

  test("dropping the middle photo then adding one keeps the later file's bytes", async () => {
    const first = shot("photo-one", ".jpg");
    const middle = shot("photo-two", ".jpg");
    const later = shot("photo-three", ".jpg");
    const added = shot("photo-four", ".jpg");
    const created = await saveSubmission(
      blank({ photos: [first, middle, later] }),
    );
    assert.deepEqual(created.photo_paths, ["A01/001.jpg", "A01/002.jpg", "A01/003.jpg"]);

    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["A01/001.jpg", "A01/003.jpg"],
        photos: [added],
      }),
    );
    assert.deepEqual(updated.photo_paths, ["A01/001.jpg", "A01/003.jpg", "A01/002.jpg"]);
    assert.equal(new Set(updated.photo_paths).size, updated.photo_paths.length);
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "photo-one");
    assert.equal((await readPhoto("A01/003.jpg"))?.bytes.toString(), "photo-three");
    assert.equal((await readPhoto("A01/002.jpg"))?.bytes.toString(), "photo-four");
  });

  test("keeping only a later photo does not let the new file reuse that name", async () => {
    const kept = shot("keep-second", ".png");
    const added = shot("brand-new", ".png");
    await saveSubmission(blank({ photos: [shot("drop-first", ".jpg"), kept] }));
    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["A01/002.png"],
        photos: [added],
      }),
    );
    assert.deepEqual(updated.photo_paths, ["A01/002.png", "A01/001.png"]);
    assert.equal((await readPhoto("A01/002.png"))?.bytes.toString(), "keep-second");
    assert.equal((await readPhoto("A01/001.png"))?.bytes.toString(), "brand-new");
  });

  test("a full prefix still continues at the next number", async () => {
    const first = shot("stay-one", ".jpg");
    const second = shot("stay-two", ".png");
    const added = shot("stay-three", ".webp");
    await saveSubmission(blank({ photos: [first, second] }));
    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["A01/001.jpg", "A01/002.png"],
        photos: [added],
      }),
    );
    assert.deepEqual(updated.photo_paths, ["A01/001.jpg", "A01/002.png", "A01/003.webp"]);
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "stay-one");
    assert.equal((await readPhoto("A01/002.png"))?.bytes.toString(), "stay-two");
    assert.equal((await readPhoto("A01/003.webp"))?.bytes.toString(), "stay-three");
  });

  test("a keep path that is an alias of 001 does not let the new file replace it", async () => {
    for (const alias of ["/A01/001.jpg", "A01/./001.jpg", "A01/../001.jpg"]) {
      const original = shot(`original-${alias}`, ".jpg");
      const added = shot(`added-${alias}`, ".jpg");
      await saveSubmission(blank({ photos: [original] }));
      const updated = await saveSubmission(
        blank({
          existingMa: "A01",
          keep_photos: [alias],
          photos: [added],
        }),
      );
      assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), `original-${alias}`);
      assert.equal((await readPhoto("A01/002.jpg"))?.bytes.toString(), `added-${alias}`);
      assert.ok(updated.photo_paths.includes(alias));
      assert.ok(updated.photo_paths.includes("A01/002.jpg"));
      fs.rmSync(path.join(tmp, "submissions.json"), { force: true });
      fs.rmSync(path.join(tmp, "photos"), { recursive: true, force: true });
      resetStoreBackendForTests();
    }
  });

  test("two new photos on a fresh mã are still 001 then 002", async () => {
    const saved = await saveSubmission(
      blank({ photos: [shot("a", ".jpg"), shot("b", ".png")] }),
    );
    assert.deepEqual(saved.photo_paths, ["A01/001.jpg", "A01/002.png"]);
  });
});
