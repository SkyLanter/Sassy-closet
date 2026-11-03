import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { getSubmission, hashBytes, readPhoto, saveSubmission, type SaveInput } from "../lib/store";

const STORE_ENV = [
  "SASSY_DATA_DIR",
  "VERCEL",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "BLOB_ACCESS",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
  "NEW_MA_WEBHOOK_URL",
  "NEW_MA_WEBHOOK_TOKEN",
] as const;

describe("rename copies kept photos onto the new mã", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-rename-"));
    for (const key of STORE_ENV) {
      prev[key] = process.env[key];
      delete process.env[key];
    }
    process.env.SASSY_DATA_DIR = tmp;
    resetStoreBackendForTests();
  });

  afterEach(() => {
    for (const key of STORE_ENV) {
      if (prev[key] === undefined) delete process.env[key];
      else process.env[key] = prev[key];
    }
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("kept bytes follow the new mã and the old file stays", async () => {
    const bytes = Buffer.from("kept-cover");
    const saved = await saveSubmission(blank({ photos: [photo(bytes, ".jpg")] }));
    assert.equal(saved.ma, "A01");
    assert.deepEqual(saved.photo_paths, ["A01/001.jpg"]);

    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["A01/001.jpg"],
        photos: [],
      }),
    );

    assert.equal(renamed.ma, "A09");
    assert.deepEqual(renamed.photo_paths, ["A09/001.jpg"]);
    assert.equal(renamed.photo_link, "Documents/Sassy Closet/Photos/A09/");
    assert.deepEqual(renamed.photo_hashes, saved.photo_hashes);
    const moved = await readPhoto("A09/001.jpg");
    assert.equal(moved?.bytes.toString(), "kept-cover");
    assert.equal(moved?.type, "image/jpeg");
    const orphan = await readPhoto("A01/001.jpg");
    assert.equal(orphan?.bytes.toString(), "kept-cover");
  });

  test("an update that keeps the mã does not move the file", async () => {
    const bytes = Buffer.from("stay-put");
    await saveSubmission(blank({ photos: [photo(bytes, ".jpg")] }));
    fs.mkdirSync(path.join(tmp, "photos", "A09"), { recursive: true });
    fs.writeFileSync(path.join(tmp, "photos", "A09", "001.jpg"), "canary-leave");

    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        color: "Den",
        keep_photos: ["A01/001.jpg"],
        photos: [],
      }),
    );

    assert.equal(updated.ma, "A01");
    assert.equal(updated.color, "Den");
    assert.deepEqual(updated.photo_paths, ["A01/001.jpg"]);
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "stay-put");
    assert.equal(fs.readFileSync(path.join(tmp, "photos", "A09", "001.jpg"), "utf8"), "canary-leave");
  });

  test("a new photo on the same mã still uses the next length-based name", async () => {
    const first = Buffer.from("already-there");
    const second = Buffer.from("appended");
    await saveSubmission(blank({ photos: [photo(first, ".jpg")] }));
    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["A01/001.jpg"],
        photos: [photo(second, ".png")],
      }),
    );
    assert.deepEqual(updated.photo_paths, ["A01/001.jpg", "A01/002.png"]);
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "already-there");
    assert.equal((await readPhoto("A01/002.png"))?.bytes.toString(), "appended");
    assert.equal(await readPhoto("A01/002.jpg"), null);
  });

  test("every kept photo moves, in order, including a png", async () => {
    const jpg = Buffer.from("cover-jpg");
    const png = Buffer.from("detail-png");
    await saveSubmission(blank({ photos: [photo(jpg, ".jpg"), photo(png, ".png")] }));
    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["A01/001.jpg", "A01/002.png"],
        photos: [],
      }),
    );
    assert.deepEqual(renamed.photo_paths, ["A09/001.jpg", "A09/002.png"]);
    assert.equal((await readPhoto("A09/001.jpg"))?.bytes.toString(), "cover-jpg");
    assert.equal((await readPhoto("A09/002.png"))?.type, "image/png");
    assert.equal((await readPhoto("A09/002.png"))?.bytes.toString(), "detail-png");
    assert.equal((await readPhoto("A01/002.png"))?.bytes.toString(), "detail-png");
  });

  test("a keep path outside the old mã stays put", async () => {
    const bytes = Buffer.from("only-a01");
    await saveSubmission(blank({ photos: [photo(bytes, ".jpg")] }));
    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["A01/001.jpg", "B02/009.jpg"],
        photos: [],
      }),
    );
    assert.deepEqual(renamed.photo_paths, ["A09/001.jpg", "B02/009.jpg"]);
    assert.equal(await readPhoto("B02/009.jpg"), null);
  });

  test("a missing kept file keeps the old path", async () => {
    const bytes = Buffer.from("gone-soon");
    await saveSubmission(blank({ photos: [photo(bytes, ".jpg")] }));
    fs.rmSync(path.join(tmp, "photos", "A01", "001.jpg"));
    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["A01/001.jpg"],
        photos: [],
      }),
    );
    assert.equal(renamed.ma, "A09");
    assert.deepEqual(renamed.photo_paths, ["A01/001.jpg"]);
    assert.equal(await readPhoto("A09/001.jpg"), null);
  });

  test("a new photo on rename is the next length-based file under the new mã", async () => {
    const kept = Buffer.from("kept-cover");
    const added = Buffer.from("added-cover");
    await saveSubmission(blank({ photos: [photo(kept, ".jpg")] }));
    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["A01/001.jpg"],
        photos: [photo(added, ".jpg")],
      }),
    );
    assert.deepEqual(renamed.photo_paths, ["A09/001.jpg", "A09/002.jpg"]);
    assert.equal((await readPhoto("A09/001.jpg"))?.bytes.toString(), "kept-cover");
    assert.equal((await readPhoto("A09/002.jpg"))?.bytes.toString(), "added-cover");
    assert.equal(renamed.photo_hashes[0], hashBytes(kept));
    assert.equal(renamed.photo_hashes[1], hashBytes(added));
  });

  test("a kept 002 is not replaced by the length-based new photo", async () => {
    const kept = Buffer.from("slot-two");
    const added = Buffer.from("brand-new");
    await saveSubmission(blank({ photos: [photo(kept, ".jpg")] }));
    const from = path.join(tmp, "photos", "A01", "001.jpg");
    const slot = path.join(tmp, "photos", "A01", "002.jpg");
    fs.copyFileSync(from, slot);
    const storeFile = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(storeFile, "utf8")) as {
      submissions: { photo_paths: string[] }[];
    };
    store.submissions[0].photo_paths = ["A01/002.jpg"];
    fs.writeFileSync(storeFile, JSON.stringify(store));

    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["A01/002.jpg"],
        photos: [photo(added, ".jpg")],
      }),
    );

    assert.deepEqual(renamed.photo_paths, ["A01/002.jpg", "A09/002.jpg"]);
    assert.equal((await readPhoto("A01/002.jpg"))?.bytes.toString(), "slot-two");
    assert.equal((await readPhoto("A09/002.jpg"))?.bytes.toString(), "brand-new");
    assert.equal(await readPhoto("A09/001.jpg"), null);
  });

  test("a slash or dot keep path stores the plain filename on the new mã", async () => {
    const bytes = Buffer.from("alias-bytes");
    await saveSubmission(blank({ photos: [photo(bytes, ".jpg")] }));
    const slash = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["/A01/001.jpg"],
        photos: [],
      }),
    );
    assert.deepEqual(slash.photo_paths, ["A09/001.jpg"]);
    assert.equal((await readPhoto("A09/001.jpg"))?.bytes.toString(), "alias-bytes");

    const dotBytes = Buffer.from("dot-bytes");
    const minted = await saveSubmission(blank({ photos: [photo(dotBytes, ".jpg")] }));
    assert.equal(minted.ma, "A10");
    const dot = await saveSubmission(
      blank({
        existingMa: "A10",
        newMa: "A11",
        keep_photos: ["A10/./001.jpg"],
        photos: [],
      }),
    );
    assert.deepEqual(dot.photo_paths, ["A11/001.jpg"]);
    assert.equal((await readPhoto("A11/001.jpg"))?.bytes.toString(), "dot-bytes");
    assert.equal((await readPhoto("A10/001.jpg"))?.bytes.toString(), "dot-bytes");
  });

  test("empty keep on rename stays empty", async () => {
    const saved = await saveSubmission(blank({ photos: [] }));
    assert.equal(saved.ma, "A01");
    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: [],
        photos: [],
      }),
    );
    assert.equal(renamed.ma, "A09");
    assert.deepEqual(renamed.photo_paths, []);
    assert.deepEqual(renamed.photo_hashes, []);
    assert.equal(renamed.photo_link, "Documents/Sassy Closet/Photos/A09/");
  });

  test("a keep path that already names the destination is not overwritten", async () => {
    const fromOld = Buffer.from("from-old");
    const already = Buffer.from("already-there");
    await saveSubmission(blank({ photos: [photo(fromOld, ".jpg")] }));
    const destDir = path.join(tmp, "photos", "A09");
    fs.mkdirSync(destDir, { recursive: true });
    fs.writeFileSync(path.join(destDir, "001.jpg"), already);

    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["A01/001.jpg", "A09/001.jpg"],
        photos: [],
      }),
    );

    assert.deepEqual(renamed.photo_paths, ["A01/001.jpg", "A09/001.jpg"]);
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "from-old");
    assert.equal((await readPhoto("A09/001.jpg"))?.bytes.toString(), "already-there");
  });

  test("different bytes already at the new path stay there", async () => {
    const fromOld = Buffer.from("from-old");
    const orphan = Buffer.from("orphan-bytes");
    await saveSubmission(blank({ photos: [photo(fromOld, ".jpg")] }));
    const destDir = path.join(tmp, "photos", "A09");
    fs.mkdirSync(destDir, { recursive: true });
    fs.writeFileSync(path.join(destDir, "001.jpg"), orphan);

    const renamed = await saveSubmission(
      blank({
        existingMa: "A01",
        newMa: "A09",
        keep_photos: ["A01/001.jpg"],
        photos: [],
      }),
    );

    assert.deepEqual(renamed.photo_paths, ["A01/001.jpg"]);
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "from-old");
    assert.equal((await readPhoto("A09/001.jpg"))?.bytes.toString(), "orphan-bytes");
  });

  test("a later rename does not replace a file another row still uses", async () => {
    const dress = Buffer.from("dress-live");
    const shirt = Buffer.from("shirt-new");
    await saveSubmission(blank({ photos: [photo(dress, ".jpg")] }));
    const storeFile = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(storeFile, "utf8")) as {
      submissions: { ma: string; photo_paths: string[] }[];
    };
    store.submissions[0].ma = "A09";
    fs.writeFileSync(storeFile, JSON.stringify(store));

    const minted = await saveSubmission(blank({ photos: [photo(shirt, ".jpg")] }));
    assert.equal(minted.ma, "A10");
    const renamed = await saveSubmission(
      blank({
        existingMa: "A10",
        newMa: "A01",
        keep_photos: ["A10/001.jpg"],
        photos: [],
      }),
    );

    assert.equal(renamed.ma, "A01");
    assert.deepEqual(renamed.photo_paths, ["A10/001.jpg"]);
    assert.equal((await readPhoto("A10/001.jpg"))?.bytes.toString(), "shirt-new");
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "dress-live");
    const earlier = await getSubmission("A09");
    assert.deepEqual(earlier?.photo_paths, ["A01/001.jpg"]);
  });

  test("a lowercase stored mã still copies the canonical photo folder", async () => {
    const bytes = Buffer.from("lower-row");
    await saveSubmission(blank({ photos: [photo(bytes, ".jpg")] }));
    const storeFile = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(storeFile, "utf8")) as {
      submissions: { ma: string }[];
    };
    store.submissions[0].ma = "a01";
    fs.writeFileSync(storeFile, JSON.stringify(store));

    const renamed = await saveSubmission(
      blank({
        existingMa: "a01",
        newMa: "A09",
        keep_photos: ["A01/001.jpg"],
        photos: [],
      }),
    );
    assert.equal(renamed.ma, "A09");
    assert.deepEqual(renamed.photo_paths, ["A09/001.jpg"]);
    assert.equal((await readPhoto("A09/001.jpg"))?.bytes.toString(), "lower-row");
  });
});

function photo(bytes: Buffer, ext: string): SaveInput["photos"][number] {
  return { bytes, hash: hashBytes(bytes), ext };
}

function blank(overrides: Partial<SaveInput> = {}): SaveInput {
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
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    ...overrides,
  };
}
