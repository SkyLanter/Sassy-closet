import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { normalizeMa } from "../lib/mint";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { exportCsv, listSubmissions, saveSubmission, type SaveInput } from "../lib/store";

const COLOR = "Xanh";

function saveInput(overrides: Partial<SaveInput> = {}): SaveInput {
  return {
    kind: "A",
    size: "M",
    link: "",
    color: "",
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

function maColumn(csv: string): string[] {
  const lines = csv.trim().split("\n").slice(1);
  return lines.map((line) => line.split(",")[0] ?? "");
}

describe("a padded new mã is stored in its canonical spelling", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "padded-new-ma-"));
    for (const key of [
      "SASSY_DATA_DIR",
      "VERCEL",
      "BLOB_READ_WRITE_TOKEN",
      "BLOB_STORE_ID",
      "BLOB_ACCESS",
      "INTAKE_DATASET_SYNC_WEBHOOK_URL",
      "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
      "NEW_MA_WEBHOOK_URL",
      "NEW_MA_WEBHOOK_TOKEN",
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

  test("extra zeros and a short S06 spelling store the canonical mã", async () => {
    const top = await saveSubmission(saveInput({ newMa: "a001" }));
    assert.equal(top.ma, "A01");
    assert.equal(top.photo_link, "Documents/Sassy Closet/Photos/A01/");

    const wide = await saveSubmission(saveInput({ kind: "A", newMa: "a0100" }));
    assert.equal(wide.ma, "A100");

    const ten = await saveSubmission(saveInput({ kind: "A", newMa: "a010" }));
    assert.equal(ten.ma, "A10");

    const otherLetter = await saveSubmission(saveInput({ kind: "A", newMa: "b010" }));
    assert.equal(otherLetter.ma, "B10");

    const widest = await saveSubmission(saveInput({ kind: "A", newMa: "b00999" }));
    assert.equal(widest.ma, "B999");

    const locked = await saveSubmission(
      saveInput({ kind: "S", newMa: " s0006 ", sell_usd: "25" }),
    );
    assert.equal(locked.ma, "S06");
    assert.equal(locked.sell_usd, "25");

    const same = await saveSubmission(
      saveInput({
        existingMa: "A01",
        newMa: "a0001",
        color: COLOR,
      }),
    );
    assert.equal(same.id, top.id);
    assert.equal(same.ma, "A01");
    assert.equal(same.color, COLOR);

    await assert.rejects(
      () => saveSubmission(saveInput({ newMa: "a0001" })),
      /đã có rồi/,
    );

    const rows = await listSubmissions();
    assert.deepEqual(
      rows.map((row) => row.ma),
      ["A01", "A100", "A10", "B10", "B999", "S06"],
    );
    assert.deepEqual(maColumn(await exportCsv()), ["A01", "A100", "A10", "B10", "B999", "S06"]);
  });

  test("a padded held mã and an off-lock S06 spelling do not create a row", async () => {
    const held = HELD_INCOMPLETE_MAS[0];
    assert.ok(held);
    const paddedHeld = `${held[0]}0${held.slice(1)}`.toLowerCase();
    assert.equal(normalizeMa(paddedHeld), held);
    assert.notEqual(paddedHeld.toUpperCase(), held);

    await assert.rejects(() => saveSubmission(saveInput({ kind: held[0], newMa: paddedHeld })), /held/);
    await assert.rejects(
      () => saveSubmission(saveInput({ kind: "S", newMa: "s006", sell_usd: "40" })),
      /s06-lock/,
    );
    await assert.rejects(
      () => saveSubmission(saveInput({ kind: "S", newMa: "s6", sell_usd: "40" })),
      /Mã mới/,
    );
    await assert.rejects(() => saveSubmission(saveInput({ kind: "A", newMa: "a1" })), /Mã mới/);
    assert.deepEqual(await listSubmissions(), []);
  });
});
