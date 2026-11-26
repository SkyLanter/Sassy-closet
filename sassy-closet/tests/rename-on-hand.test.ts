import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { lookupMaCard } from "../lib/ma-card";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { getOnHandRows, hashBytes, saveSubmission } from "../lib/store";
import type { SaveInput } from "../lib/store";

const ENV = [
  "SASSY_DATA_DIR",
  "VERCEL",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "BLOB_ACCESS",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
] as const;

describe("renaming an intake mã keeps its on-hand rows", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-on-hand-"));
    for (const key of ENV) {
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

  test("the find card for the new mã still has the old on-hand row", async () => {
    const created = await saveSubmission(input("Kem"));
    assert.equal(created.ma, "A01");
    writeOnHand({
      A01: [{ size: "M", color: "Kem", qty_on_hand: 1, status: "on_hand" }],
    });

    const renamed = await saveSubmission(
      input("Kem", { existingMa: "A01", newMa: "A09", keep_photos: created.photo_paths }),
    );
    assert.equal(renamed.ma, "A09");

    const card = await lookupMaCard("A09");
    assert.equal(card?.staged_only, false);
    assert.equal(card?.on_hand.length, 1);
    assert.equal(card?.on_hand[0].size, "M");
    assert.equal(card?.on_hand[0].qty_on_hand, 1);
    assert.equal(card?.on_hand[0].where_stored, "Documents/Sassy Closet/Photos/A09/");

    const disk = readStore();
    assert.deepEqual(Object.keys(disk.on_hand ?? {}).sort(), ["A09"]);
    assert.equal((await getOnHandRows("A01")).length, 0);
  });

  test("an in-place save leaves the on-hand bucket on the same mã", async () => {
    const created = await saveSubmission(input("Kem"));
    writeOnHand({
      A01: [{ size: "M", color: "Kem", qty_on_hand: 2, status: "reserved" }],
    });
    const updated = await saveSubmission(
      input("Đen", { existingMa: created.ma, keep_photos: created.photo_paths }),
    );
    assert.equal(updated.ma, "A01");
    assert.equal(updated.color, "Đen");
    const rows = await getOnHandRows("A01");
    assert.equal(rows.length, 1);
    assert.equal(rows[0].qty_on_hand, 2);
    assert.equal(rows[0].status, "reserved");
  });

  test("a bucket already stored on the new mã is not replaced", async () => {
    const created = await saveSubmission(input("Kem"));
    writeOnHand({
      A01: [{ size: "M", color: "Kem", qty_on_hand: 1, status: "on_hand" }],
      A09: [{ size: "S", color: "Đen", qty_on_hand: 4, status: "sold" }],
    });
    await saveSubmission(input("Kem", { existingMa: "A01", newMa: "A09", keep_photos: created.photo_paths }));
    const rows = await getOnHandRows("A09");
    assert.equal(rows.length, 1);
    assert.equal(rows[0].size, "S");
    assert.equal(rows[0].qty_on_hand, 4);
    const disk = readStore();
    assert.equal(disk.on_hand?.A01?.[0]?.size, "M");
    assert.equal(disk.on_hand?.A09?.[0]?.size, "S");
  });
});

function input(color: string, extra: Partial<SaveInput> = {}): SaveInput {
  const bytes = Buffer.from(`photo-${color}`);
  return {
    kind: "A",
    size: "M",
    link: "",
    color,
    color_note: "",
    pieces: [],
    cost_usd: "",
    cost_cny: "",
    cost_currency: "USD",
    sell_usd: "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: [],
    photos: extra.keep_photos ? [] : [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    ...extra,
  };
}

type OnHandFile = {
  on_hand?: Record<string, { size?: string }[]>;
};

function storePath(): string {
  return path.join(process.env.SASSY_DATA_DIR ?? "", "submissions.json");
}

function writeOnHand(onHand: Record<string, unknown>): void {
  const disk = JSON.parse(fs.readFileSync(storePath(), "utf8")) as OnHandFile;
  disk.on_hand = onHand as OnHandFile["on_hand"];
  fs.writeFileSync(storePath(), JSON.stringify(disk));
  resetStoreBackendForTests();
}

function readStore(): OnHandFile {
  return JSON.parse(fs.readFileSync(storePath(), "utf8")) as OnHandFile;
}
