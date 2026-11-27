import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { listSubmissions, saveSubmission, type SaveInput } from "../lib/store";

/**
 * An update used to replace every row with the same numeric id. Two rows that
 * already shared an id (a stale nextId, or two saves that read the file
 * together) meant editing one mã rewrote the other mã as a copy of it.
 */
describe("editing one intake row does not overwrite a row with the same id", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-same-id-"));
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

  test("saving A02 leaves A01 when both rows were stored with the same id", async () => {
    await saveSubmission(input("Kem", "A01"));
    const second = await saveSubmission(input("Đen", "A02"));
    const file = storePath();
    const disk = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: { id: number; ma: string; color: string }[];
    };
    assert.equal(disk.submissions[0].ma, "A01");
    assert.equal(disk.submissions[1].ma, "A02");
    disk.submissions[1].id = disk.submissions[0].id;
    fs.writeFileSync(file, JSON.stringify(disk));
    resetStoreBackendForTests();

    const edited = await saveSubmission(
      input("Xanh", "A02", { existingMa: "A02", keep_photos: second.photo_paths, photos: [] }),
    );
    assert.equal(edited.ma, "A02");
    assert.equal(edited.color, "Xanh");

    const rows = await listSubmissions();
    assert.deepEqual(
      rows.map((row) => row.ma),
      ["A01", "A02"],
    );
    assert.equal(rows[0].color, "Kem");
    assert.equal(rows[0].size, "M");
    assert.equal(rows[1].color, "Xanh");
    assert.equal(rows[1].size, "L");
  });

  test("two distinct ids still update only the mã being saved", async () => {
    await saveSubmission(input("Kem", "A01"));
    const second = await saveSubmission(input("Đen", "A02"));
    await saveSubmission(
      input("Xanh", "A02", { existingMa: second.ma, keep_photos: second.photo_paths, photos: [] }),
    );
    const rows = await listSubmissions();
    assert.deepEqual(
      rows.map((row) => `${row.ma}:${row.color}`),
      ["A01:Kem", "A02:Xanh"],
    );
  });
});

function input(color: string, ma: string, extra: Partial<SaveInput> = {}): SaveInput {
  return {
    kind: "A",
    size: extra.existingMa ? "L" : "M",
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
    photos: [],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    newMa: extra.existingMa ? undefined : ma,
    ...extra,
  };
}

function storePath(): string {
  return path.join(process.env.SASSY_DATA_DIR ?? "", "submissions.json");
}
