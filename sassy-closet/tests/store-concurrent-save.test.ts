import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { getFx, hashBytes, listSubmissions, saveSubmission, setFx, type SaveInput } from "../lib/store";

const ENV = [
  "SASSY_DATA_DIR",
  "VERCEL",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "BLOB_ACCESS",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
] as const;

describe("intake saves do not drop a row written at the same time", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-concurrent-"));
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

  test("two new mãs saved together both stay on disk", async () => {
    const [first, second] = await Promise.all([
      saveSubmission(input("Kem")),
      saveSubmission(input("Đen")),
    ]);
    const rows = await listSubmissions();
    assert.equal(rows.length, 2);
    assert.notEqual(first.ma, second.ma);
    assert.deepEqual(rows.map((row) => row.ma).sort(), [first.ma, second.ma].sort());
    assert.deepEqual(rows.map((row) => row.color).sort(), ["Kem", "Đen"]);
  });

  test("two saves of one free mã cannot both succeed", async () => {
    await assert.rejects(
      Promise.all([
        saveSubmission(input("Kem", { newMa: "Q05" })),
        saveSubmission(input("Đen", { newMa: "Q05" })),
      ]),
      (error: unknown) => {
        assert.equal((error as { status?: number }).status, 409);
        return true;
      },
    );
    const rows = await listSubmissions();
    assert.equal(rows.length, 1);
    assert.equal(rows[0].ma, "Q05");
    assert.equal(rows[0].color, "Kem");
  });

  test("a rate update in the same turn does not erase the new row or the rate", async () => {
    const [saved, fx] = await Promise.all([saveSubmission(input("Kem")), setFx(7.25)]);
    const rows = await listSubmissions();
    assert.equal(rows.length, 1);
    assert.equal(rows[0].ma, saved.ma);
    assert.equal(rows[0].color, "Kem");
    assert.equal(fx.usd_cny, 7.25);
    assert.equal((await getFx()).usd_cny, 7.25);
    const disk = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
      submissions: { ma: string }[];
      fx: { usd_cny: number };
    };
    assert.equal(disk.submissions.length, 1);
    assert.equal(disk.fx.usd_cny, 7.25);
  });
});

function input(color: string, extra: Partial<SaveInput> = {}): SaveInput {
  const bytes = Buffer.from(`photo-${color}`);
  return {
    kind: "Q",
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
    photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    ...extra,
  };
}
