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
import { exportCsv, findByPhotoHash, getOnHandRows, getSubmission, hashBytes, listSubmissions, readPhoto, saveSubmission } from "../lib/store";

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
    assert.match(csv, /kind_vi/);
    assert.match(csv, /size_options/);
    assert.match(csv, /2XS XS S M L XL 2XL/);
    assert.ok(!csv.includes("qty"));

    const disk = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
      submissions: { ma: string }[];
    };
    assert.equal(disk.submissions.length, 1);
    assert.ok(fs.existsSync(path.join(tmp, "photos", "A01", "001.jpg")));
  });

  test("kind G will not mint held G01; shoe G02 saves with size_options 35–41", async () => {
    await assert.rejects(
      saveSubmission({
        kind: "G",
        size: "37 38",
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
      }),
      /Không mint G01 \(held\)/,
    );
    const saved = await saveSubmission({
      kind: "G",
      size: "37 38",
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
      newMa: "G02",
    });
    assert.equal(saved.ma, "G02");
    assert.equal(saved.kind, "G");
    assert.equal(saved.size, "37 38");
    const csv = await exportCsv();
    assert.match(csv, /G02/);
    assert.match(csv, /Giày \/ Cao gót/);
    assert.match(csv, /35 36 37 38 39 40 41/);
    const listed = await listSubmissions();
    assert.equal(listed.length, 1);
    assert.equal(listed[0].ma, "G02");
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
    assert.equal(saved.sell_usd, "");
    assert.equal(saved.sell_cny, "");
    assert.equal(saved.price, "");
    assert.equal(saved.auto_price ?? null, null);
    assert.match(saved.caption_vi, /Inbox giá/);
    assert.doesNotMatch(saved.caption_vi, /\$\d/);
    const listed = await listSubmissions();
    assert.equal(listed.length, 1);
    assert.equal(listed[0].ma, "D01");
  });

  test("blank sell price saves S06 and does not invent a calculated sell", async () => {
    const saved = await saveSubmission({
      kind: "S",
      size: "M",
      link: "",
      color: "Den",
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
      newMa: "S06",
    });
    assert.equal(saved.ma, "S06");
    assert.equal(saved.sell_usd, "");
    assert.equal(saved.price, "");
    assert.equal(saved.auto_price ?? null, null);
    assert.match(saved.caption_vi, /Inbox giá/);
    assert.doesNotMatch(saved.caption_vi, /\$\d/);
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

  test("on-hand rows stored under a padded mã are found for A01 and a001", async () => {
    await saveSubmission({
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
    });
    const file = path.join(tmp, "submissions.json");
    const disk = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: { ma: string }[];
      on_hand?: unknown;
    };
    assert.equal(disk.submissions[0].ma, "A01");
    disk.on_hand = {
      A001: [{ size: "M", color: "Kem", qty_on_hand: 1, status: "on_hand" }],
    };
    fs.writeFileSync(file, JSON.stringify(disk));
    const brief = async (ma: string) =>
      (await getOnHandRows(ma)).map((row) => ({
        qty_on_hand: row.qty_on_hand,
        status: row.status,
      }));
    assert.deepEqual(
      { A01: await brief("A01"), a001: await brief("a001") },
      {
        A01: [{ qty_on_hand: 1, status: "on_hand" }],
        a001: [{ qty_on_hand: 1, status: "on_hand" }],
      },
    );
  });

  test("an exact canonical on-hand key wins over a padded alias", async () => {
    await saveSubmission({
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
    });
    const file = path.join(tmp, "submissions.json");
    const disk = JSON.parse(fs.readFileSync(file, "utf8")) as { on_hand?: unknown };
    disk.on_hand = {
      A01: [{ qty_on_hand: 2, status: "on_hand" }],
      A001: [{ qty_on_hand: 9, status: "sold" }],
    };
    fs.writeFileSync(file, JSON.stringify(disk));
    const rows = await getOnHandRows("A01");
    assert.equal(rows.length, 1);
    assert.equal(rows[0].qty_on_hand, 2);
    assert.equal(rows[0].status, "on_hand");
  });

  test("a new photo does not reuse a kept higher index, and the removed hash is dropped", async () => {
    const one = Buffer.from("photo-one");
    const two = Buffer.from("photo-two");
    const three = Buffer.from("photo-three");
    const four = Buffer.from("photo-four");
    const saved = await saveSubmission({
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
      photos: [
        { bytes: one, hash: hashBytes(one), ext: ".jpg" },
        { bytes: two, hash: hashBytes(two), ext: ".jpg" },
        { bytes: three, hash: hashBytes(three), ext: ".jpg" },
      ],
    });
    assert.deepEqual(saved.photo_paths, ["A01/001.jpg", "A01/002.jpg", "A01/003.jpg"]);
    const updated = await saveSubmission({
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
      existingMa: "A01",
      keep_photos: ["A01/001.jpg", "A01/003.jpg"],
      photos: [{ bytes: four, hash: hashBytes(four), ext: ".jpg" }],
    });
    const kept = await readPhoto("A01/003.jpg");
    const added = await readPhoto("A01/004.jpg");
    assert.deepEqual(
      {
        photo_paths: updated.photo_paths,
        kept003: kept?.bytes.toString() ?? null,
        added004: added?.bytes.toString() ?? null,
        removedPhotoTwo: (await findByPhotoHash(hashBytes(two))).length,
        keptPhotoThree: (await findByPhotoHash(hashBytes(three))).length,
      },
      {
        photo_paths: ["A01/001.jpg", "A01/003.jpg", "A01/004.jpg"],
        kept003: "photo-three",
        added004: "photo-four",
        removedPhotoTwo: 0,
        keptPhotoThree: 1,
      },
    );
  });

  test("keeping every photo and adding one more still writes the next index", async () => {
    const one = Buffer.from("photo-one");
    const two = Buffer.from("photo-two");
    const three = Buffer.from("photo-three");
    const five = Buffer.from("photo-five");
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
      photos: [
        { bytes: one, hash: hashBytes(one), ext: ".jpg" },
        { bytes: two, hash: hashBytes(two), ext: ".jpg" },
        { bytes: three, hash: hashBytes(three), ext: ".jpg" },
      ],
    });
    const updated = await saveSubmission({
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
      existingMa: "A01",
      keep_photos: ["A01/001.jpg", "A01/002.jpg", "A01/003.jpg"],
      photos: [{ bytes: five, hash: hashBytes(five), ext: ".jpg" }],
    });
    assert.deepEqual(updated.photo_paths, [
      "A01/001.jpg",
      "A01/002.jpg",
      "A01/003.jpg",
      "A01/004.jpg",
    ]);
    assert.equal((await readPhoto("A01/001.jpg"))?.bytes.toString(), "photo-one");
    assert.equal((await readPhoto("A01/002.jpg"))?.bytes.toString(), "photo-two");
    assert.equal((await readPhoto("A01/003.jpg"))?.bytes.toString(), "photo-three");
    assert.equal((await readPhoto("A01/004.jpg"))?.bytes.toString(), "photo-five");
  });

  test("missing Blob store/photo is empty, not a crash", () => {
    assert.equal(isMissingBlobError(new BlobNotFoundError()), true);
    assert.equal(isMissingBlobError({ name: "BlobNotFoundError" }), true);
    assert.equal(isMissingBlobError(new BlobError("Failed to fetch blob: 404 Not Found")), true);
    assert.equal(isMissingBlobError(new Error("Failed to fetch blob: 403 Forbidden")), false);
    assert.equal(isMissingBlobError(new Error("Kho mã đọc lỗi — không ghi đè.")), false);
  });
});
