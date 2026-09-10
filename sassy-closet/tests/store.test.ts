import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { BlobError, BlobNotFoundError } from "@vercel/blob";
import {
  copyStoreAndPhotos,
  createLocalBackend,
  isMissingBlobError,
  parseStore,
  resetStoreBackendForTests,
  sanitizePhotoRel,
  storageMode,
  storageStatus,
} from "../lib/store-backend";
import { exportCsv, findByPhotoHash, getSubmission, hashBytes, listSubmissions, readPhoto, saveSubmission } from "../lib/store";

describe("durable / local store", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-store-"));
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

  test("storageMode is local without Blob, ephemeral on Vercel, durable with Blob env", () => {
    assert.equal(storageMode(), "local");
    process.env.VERCEL = "1";
    assert.equal(storageMode(), "ephemeral");
    assert.equal(storageStatus().durable, false);
    process.env.BLOB_STORE_ID = "store_test";
    assert.equal(storageMode(), "durable");
    assert.equal(storageStatus().durable, true);
  });

  test("save + list + get + photo + export stay on local disk (no invented mã)", async () => {
    const bytes = Buffer.from("fake-jpeg-a01");
    const saved = await saveSubmission({
      kind: "A",
      size: "M",
      link: "https://e.tb.cn/example",
      color: "Kem",
      color_note: "",
      pieces: [],
      cost_usd: "12",
      cost_cny: "",
      cost_currency: "USD",
      sell_usd: "28",
      sell_cny: "",
      sell_currency: "USD",
      keep_photos: [],
      photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    });
    assert.equal(saved.ma, "A01");
    assert.deepEqual(saved.photo_paths, ["A01/001.jpg"]);
    assert.equal(saved.status, "staged");
    assert.equal(saved.square, "not_square");

    const listed = await listSubmissions();
    assert.equal(listed.length, 1);
    assert.equal(listed[0].ma, "A01");

    const fetched = await getSubmission("a01");
    assert.equal(fetched?.color, "Kem");
    assert.equal(fetched?.cost_usd, "12");

    const photo = await readPhoto("A01/001.jpg");
    assert.ok(photo);
    assert.equal(photo.type, "image/jpeg");
    assert.equal(photo.bytes.toString(), "fake-jpeg-a01");

    const csv = await exportCsv();
    assert.match(csv, /^ma,/);
    assert.match(csv, /A01/);
    assert.match(csv, /https:\/\/e\.tb\.cn\/example/);
    assert.ok(!csv.includes("qty"));

    const disk = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
      submissions: { ma: string }[];
    };
    assert.equal(disk.submissions.length, 1);
    assert.ok(fs.existsSync(path.join(tmp, "photos", "A01", "001.jpg")));
  });

  test("kind D mints D01 and does not invent extra mãs", async () => {
    const saved = await saveSubmission({
      kind: "D",
      size: "",
      link: "",
      color: "Đen",
      color_note: "",
      pieces: [],
      cost_usd: "12",
      cost_cny: "80.52",
      cost_currency: "USD",
      sell_usd: "",
      sell_cny: "",
      sell_currency: "USD",
      keep_photos: [],
      photos: [],
    });
    assert.equal(saved.ma, "D01");
    assert.equal(saved.kind, "D");
    const listed = await listSubmissions();
    assert.equal(listed.length, 1);
    assert.equal(listed[0].ma, "D01");
  });

  test("second save mints A02 and find-by-hash only matches the real photo", async () => {
    const first = Buffer.from("photo-one");
    const second = Buffer.from("photo-two");
    await saveSubmission({
      kind: "A",
      size: "",
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
      photos: [{ bytes: first, hash: hashBytes(first), ext: ".jpg" }],
    });
    const saved = await saveSubmission({
      kind: "A",
      size: "",
      link: "",
      color: "Trắng",
      color_note: "",
      pieces: [],
      cost_usd: "",
      cost_cny: "",
      cost_currency: "USD",
      sell_usd: "",
      sell_cny: "",
      sell_currency: "USD",
      keep_photos: [],
      photos: [{ bytes: second, hash: hashBytes(second), ext: ".png" }],
    });
    assert.equal(saved.ma, "A02");
    const hits = await findByPhotoHash(hashBytes(second));
    assert.equal(hits.length, 1);
    assert.equal(hits[0].ma, "A02");
    assert.equal((await findByPhotoHash("nope")).length, 0);
  });

  test("copyStoreAndPhotos migrates metadata and bytes to another disk backend", async () => {
    const bytes = Buffer.from("migrate-me");
    await saveSubmission({
      kind: "Q",
      size: "S",
      link: "",
      color: "Xanh",
      color_note: "ghi chú thật",
      pieces: [],
      cost_usd: "",
      cost_cny: "80",
      cost_currency: "CNY",
      sell_usd: "",
      sell_cny: "",
      sell_currency: "USD",
      keep_photos: [],
      photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    });
    const destRoot = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-dest-"));
    try {
      const copied = await copyStoreAndPhotos(createLocalBackend(tmp), createLocalBackend(destRoot));
      assert.equal(copied.submissions, 1);
      assert.equal(copied.photos, 1);
      const dest = createLocalBackend(destRoot);
      const store = await dest.readStore();
      assert.equal(store?.submissions[0].ma, "Q01");
      assert.equal(store?.submissions[0].color_note, "ghi chú thật");
      const photo = await dest.readPhoto("Q01/001.jpg");
      assert.equal(photo?.bytes.toString(), "migrate-me");
    } finally {
      fs.rmSync(destRoot, { recursive: true, force: true });
    }
  });

  test("copyStoreAndPhotos does not invent rows when source is empty", async () => {
    const destRoot = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-empty-"));
    try {
      const copied = await copyStoreAndPhotos(createLocalBackend(tmp), createLocalBackend(destRoot));
      assert.deepEqual(copied, { submissions: 0, photos: 0 });
      assert.equal(await createLocalBackend(destRoot).readStore(), null);
    } finally {
      fs.rmSync(destRoot, { recursive: true, force: true });
    }
  });

  test("parseStore refuses to treat garbage as an empty closet", () => {
    assert.throws(() => parseStore("{not-json"), /không ghi đè/);
    assert.throws(() => parseStore("{}"), /không đúng dạng/);
    const ok = parseStore('{"nextId":3,"submissions":[{"ma":"P01"}],"fx":{"usd_cny":6.7,"updated":"2026-09-08"}}');
    assert.equal(ok.submissions[0].ma, "P01");
    assert.equal(ok.nextId, 3);
  });

  test("sanitizePhotoRel strips traversal", () => {
    assert.equal(sanitizePhotoRel("A01/001.jpg"), "A01/001.jpg");
    assert.ok(!sanitizePhotoRel("/A01/../secret.jpg").includes(".."));
  });

  test("local backend rejects photo paths outside photos/", async () => {
    const backend = createLocalBackend(tmp);
    const escaped = await backend.readPhoto("../submissions.json");
    assert.equal(escaped, null);
  });

  test("missing Blob store/photo is empty, not a crash", () => {
    assert.equal(isMissingBlobError(new BlobNotFoundError()), true);
    assert.equal(isMissingBlobError({ name: "BlobNotFoundError" }), true);
    assert.equal(isMissingBlobError(new BlobError("Failed to fetch blob: 404 Not Found")), true);
    assert.equal(isMissingBlobError(new Error("Failed to fetch blob: 403 Forbidden")), false);
    assert.equal(isMissingBlobError(new Error("Kho mã đọc lỗi — không ghi đè.")), false);
  });
});
