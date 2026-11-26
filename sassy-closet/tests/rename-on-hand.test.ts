import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { getOnHandRows, saveSubmission } from "../lib/store";
import type { SaveInput } from "../lib/store";

describe("rename keeps on-hand quantities", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-rename-qty-"));
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

  test("quantities stored under a variant key follow the mã and a zero qty stays", async () => {
    await saveSubmission(input());
    writeOnHand({
      a01: [{ size: "M", color: "Kem", qty_on_hand: 0, status: "on_hand" }],
      A03: [{ size: "S", color: "Đen", qty: 1, status: "reserved" }],
    });

    const renamed = await saveSubmission({ ...input(), existingMa: "A01", newMa: "A03" });
    assert.equal(renamed.ma, "A03");

    const moved = await getOnHandRows("A03");
    assert.deepEqual(
      moved.map((row) => [row.size, row.qty_on_hand, row.status]),
      [
        ["S", 1, "reserved"],
        ["M", 0, "on_hand"],
      ],
    );
    assert.equal((await getOnHandRows("A01")).length, 0);
    assert.equal((await getOnHandRows("a01")).length, 0);

    const disk = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
      on_hand?: Record<string, unknown>;
    };
    assert.deepEqual(Object.keys(disk.on_hand ?? {}).sort(), ["A03"]);
  });

  test("saving the same mã does not copy quantities onto another code", async () => {
    await saveSubmission(input());
    writeOnHand({ A01: [{ size: "M", qty_on_hand: 2, status: "on_hand" }] });
    const saved = await saveSubmission({ ...input(), existingMa: "a01", size: "L" });
    assert.equal(saved.ma, "A01");
    assert.equal((await getOnHandRows("A01"))[0]?.qty_on_hand, 2);
    assert.equal((await getOnHandRows("A02")).length, 0);
  });
});

function writeOnHand(onHand: Record<string, unknown>): void {
  const file = path.join(process.env.SASSY_DATA_DIR ?? "", "submissions.json");
  const disk = JSON.parse(fs.readFileSync(file, "utf8")) as { on_hand?: unknown };
  disk.on_hand = onHand;
  fs.writeFileSync(file, JSON.stringify(disk));
  resetStoreBackendForTests();
}

function input(): SaveInput {
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
  };
}
