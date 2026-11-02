import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { findByPhotoHash, hashBytes, saveSubmission } from "../lib/store";
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

describe("find-mã after a photo is dropped", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-drop-photo-"));
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

  test("keeping one photo drops the other hash so find-mã misses the removed photo", async () => {
    const first = Buffer.from("photo-one");
    const second = Buffer.from("photo-two");
    const firstHash = hashBytes(first);
    const secondHash = hashBytes(second);
    const created = await saveSubmission(
      blank({
        photos: [
          { bytes: first, hash: firstHash, ext: ".jpg" },
          { bytes: second, hash: secondHash, ext: ".png" },
        ],
      }),
    );
    assert.deepEqual(created.photo_paths, ["A01/001.jpg", "A01/002.png"]);
    assert.deepEqual(created.photo_hashes, [firstHash, secondHash]);

    const updated = await saveSubmission(
      blank({
        existingMa: created.ma,
        keep_photos: ["A01/001.jpg"],
      }),
    );
    assert.deepEqual(updated.photo_paths, ["A01/001.jpg"]);
    assert.deepEqual(updated.photo_hashes, [firstHash]);

    const kept = await findByPhotoHash(firstHash);
    assert.equal(kept.length, 1);
    assert.equal(kept[0].ma, "A01");
    assert.equal((await findByPhotoHash(secondHash)).length, 0);

    const form = new FormData();
    form.set("photo", new File([second], "gone.png", { type: "image/png" }));
    const { POST } = await import("../app/api/find-ma/route");
    const res = await POST(new Request("http://localhost/api/find-ma", { method: "POST", body: form }));
    assert.equal(res.status, 200);
    const body = (await res.json()) as { matches: { ma: string }[] };
    assert.deepEqual(body.matches, []);
  });

  test("keeping only the later photo keeps that photo's hash, not the earlier index", async () => {
    const first = Buffer.from("earlier");
    const second = Buffer.from("later");
    const firstHash = hashBytes(first);
    const secondHash = hashBytes(second);
    await saveSubmission(
      blank({
        photos: [
          { bytes: first, hash: firstHash, ext: ".jpg" },
          { bytes: second, hash: secondHash, ext: ".png" },
        ],
      }),
    );
    const onlyLater = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["A01/002.png"],
      }),
    );
    assert.deepEqual(onlyLater.photo_paths, ["A01/002.png"]);
    assert.deepEqual(onlyLater.photo_hashes, [secondHash]);
    assert.equal((await findByPhotoHash(firstHash)).length, 0);
    assert.equal((await findByPhotoHash(secondHash))[0]?.ma, "A01");
  });

  test("kept hashes follow keep_photos order when both photos stay", async () => {
    const first = Buffer.from("order-a");
    const second = Buffer.from("order-b");
    const firstHash = hashBytes(first);
    const secondHash = hashBytes(second);
    await saveSubmission(
      blank({
        photos: [
          { bytes: first, hash: firstHash, ext: ".jpg" },
          { bytes: second, hash: secondHash, ext: ".png" },
        ],
      }),
    );
    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["A01/002.png", "A01/001.jpg"],
      }),
    );
    assert.deepEqual(updated.photo_paths, ["A01/002.png", "A01/001.jpg"]);
    assert.deepEqual(updated.photo_hashes, [secondHash, firstHash]);
  });

  test("keeping none clears every old hash", async () => {
    const only = Buffer.from("only-photo");
    const hash = hashBytes(only);
    await saveSubmission(blank({ photos: [{ bytes: only, hash, ext: ".jpg" }] }));
    const updated = await saveSubmission(blank({ existingMa: "A01", keep_photos: [] }));
    assert.deepEqual(updated.photo_paths, []);
    assert.deepEqual(updated.photo_hashes, []);
    assert.equal((await findByPhotoHash(hash)).length, 0);
  });

  test("keeping every photo still finds each one", async () => {
    const first = Buffer.from("keep-a");
    const second = Buffer.from("keep-b");
    const firstHash = hashBytes(first);
    const secondHash = hashBytes(second);
    const created = await saveSubmission(
      blank({
        photos: [
          { bytes: first, hash: firstHash, ext: ".jpg" },
          { bytes: second, hash: secondHash, ext: ".png" },
        ],
      }),
    );
    const updated = await saveSubmission(
      blank({ existingMa: "A01", keep_photos: [...created.photo_paths] }),
    );
    assert.deepEqual(updated.photo_hashes, [firstHash, secondHash]);
    assert.equal((await findByPhotoHash(firstHash)).length, 1);
    assert.equal((await findByPhotoHash(secondHash)).length, 1);
  });

  test("a new photo appended after a drop does not revive the removed hash", async () => {
    const first = Buffer.from("stay");
    const dropped = Buffer.from("drop-me");
    const added = Buffer.from("brand-new");
    const firstHash = hashBytes(first);
    const droppedHash = hashBytes(dropped);
    const addedHash = hashBytes(added);
    await saveSubmission(
      blank({
        photos: [
          { bytes: first, hash: firstHash, ext: ".jpg" },
          { bytes: dropped, hash: droppedHash, ext: ".png" },
        ],
      }),
    );
    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["A01/001.jpg"],
        photos: [{ bytes: added, hash: addedHash, ext: ".webp" }],
      }),
    );
    assert.deepEqual(updated.photo_paths, ["A01/001.jpg", "A01/002.webp"]);
    assert.deepEqual(updated.photo_hashes, [firstHash, addedHash]);
    assert.equal((await findByPhotoHash(droppedHash)).length, 0);
    assert.equal((await findByPhotoHash(addedHash))[0]?.ma, "A01");
  });

  test("dropping a shared photo from one mã leaves the other mã's copy findable", async () => {
    const shared = Buffer.from("shared-bytes");
    const extra = Buffer.from("extra-bytes");
    const sharedHash = hashBytes(shared);
    const extraHash = hashBytes(extra);
    await saveSubmission(blank({ photos: [{ bytes: shared, hash: sharedHash, ext: ".jpg" }] }));
    await saveSubmission(
      blank({
        color: "Đen",
        photos: [
          { bytes: shared, hash: sharedHash, ext: ".jpg" },
          { bytes: extra, hash: extraHash, ext: ".png" },
        ],
      }),
    );
    await saveSubmission(
      blank({
        existingMa: "A02",
        color: "Đen",
        keep_photos: ["A02/002.png"],
      }),
    );
    const hits = await findByPhotoHash(sharedHash);
    assert.deepEqual(
      hits.map((row) => row.ma),
      ["A01"],
    );
    assert.equal((await findByPhotoHash(extraHash))[0]?.ma, "A02");
  });

  test("a keep path with no stored hash does not shift a photo added in the same save", async () => {
    const first = Buffer.from("aligned-one");
    const added = Buffer.from("aligned-new");
    const firstHash = hashBytes(first);
    const addedHash = hashBytes(added);
    await saveSubmission(blank({ photos: [{ bytes: first, hash: firstHash, ext: ".jpg" }] }));
    const updated = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["A01/001.jpg", "A01/missing.jpg"],
        photos: [{ bytes: added, hash: addedHash, ext: ".png" }],
      }),
    );
    assert.deepEqual(updated.photo_paths, ["A01/001.jpg", "A01/missing.jpg", "A01/003.png"]);
    assert.deepEqual(updated.photo_hashes, [firstHash, "", addedHash]);
    assert.equal((await findByPhotoHash(addedHash))[0]?.ma, "A01");
    assert.equal((await findByPhotoHash(firstHash))[0]?.ma, "A01");
    assert.equal((await findByPhotoHash("")).length, 0);
  });

  test("a new mã with a stray keep path does not store the upload hash on that path", async () => {
    const added = Buffer.from("create-with-keep");
    const addedHash = hashBytes(added);
    const created = await saveSubmission(
      blank({
        keep_photos: ["A01/not-uploaded.jpg"],
        photos: [{ bytes: added, hash: addedHash, ext: ".jpg" }],
      }),
    );
    assert.deepEqual(created.photo_paths, ["A01/not-uploaded.jpg", "A01/002.jpg"]);
    assert.deepEqual(created.photo_hashes, ["", addedHash]);

    const edited = await saveSubmission(
      blank({
        existingMa: "A01",
        keep_photos: ["A01/002.jpg"],
      }),
    );
    assert.deepEqual(edited.photo_paths, ["A01/002.jpg"]);
    assert.deepEqual(edited.photo_hashes, [addedHash]);
    assert.equal((await findByPhotoHash(addedHash))[0]?.ma, "A01");
  });

  test("a row with a missing photo_hashes array does not fail the search", async () => {
    const bad = Buffer.from("bad-row");
    const good = Buffer.from("good-row");
    const badHash = hashBytes(bad);
    const goodHash = hashBytes(good);
    await saveSubmission(blank({ photos: [{ bytes: bad, hash: badHash, ext: ".jpg" }] }));
    await saveSubmission(
      blank({ color: "Đen", photos: [{ bytes: good, hash: goodHash, ext: ".jpg" }] }),
    );
    const file = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: Submission[];
    };
    delete (store.submissions[0] as { photo_hashes?: string[] }).photo_hashes;
    fs.writeFileSync(file, JSON.stringify(store));
    resetStoreBackendForTests();

    const hits = await findByPhotoHash(goodHash);
    assert.deepEqual(
      hits.map((row) => row.ma),
      ["A02"],
    );
    assert.equal((await findByPhotoHash(badHash)).length, 0);
  });

  test("a repeated path keeps the first stored hash, and an extra stale hash is not copied", async () => {
    const first = Buffer.from("path-one");
    const firstHash = hashBytes(first);
    await saveSubmission(blank({ photos: [{ bytes: first, hash: firstHash, ext: ".jpg" }] }));
    const file = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: Submission[];
    };
    const row = store.submissions[0];
    row.photo_paths = ["A01/001.jpg", "A01/001.jpg"];
    row.photo_hashes = [firstHash, "stale-second-hash", "orphan-with-no-path"];
    fs.writeFileSync(file, JSON.stringify(store));
    resetStoreBackendForTests();

    const updated = await saveSubmission(
      blank({ existingMa: "A01", keep_photos: ["A01/001.jpg"] }),
    );
    assert.deepEqual(updated.photo_hashes, [firstHash]);
    assert.equal((await findByPhotoHash("stale-second-hash")).length, 0);
    assert.equal((await findByPhotoHash("orphan-with-no-path")).length, 0);
  });
});
