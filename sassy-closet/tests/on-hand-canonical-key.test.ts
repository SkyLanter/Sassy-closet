import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { lookupMaCard } from "../lib/ma-card";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { getOnHandRows, saveSubmission, type SaveInput } from "../lib/store";

/**
 * The find card asks for the canonical mã. On-hand rows filed under another
 * spelling of that same mã ("a01", "A001") were missed, so the card said
 * staged-only while the quantity was in the file.
 */
describe("find card reads on-hand by canonical mã", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-on-hand-key-"));
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

  test("a lowercase key is the A01 card, including a zero qty", async () => {
    await saveSubmission(input());
    writeOnHand({
      a01: [{ size: "M", color: "Kem", qty_on_hand: 0, status: "on_hand" }],
      B02: [{ size: "S", color: "Đen", qty_on_hand: 9, status: "sold" }],
    });

    const card = await lookupMaCard("A01");
    assert.equal(card?.staged_only, false);
    assert.equal(card?.on_hand.length, 1);
    assert.equal(card?.on_hand[0].size, "M");
    assert.equal(card?.on_hand[0].qty_on_hand, 0);
    assert.equal(card?.on_hand[0].status, "on_hand");
    assert.equal((await getOnHandRows("B02"))[0]?.qty_on_hand, 9);
  });

  test("a padded key is the same mã, and the canonical key wins when both exist", async () => {
    await saveSubmission(input());
    writeOnHand({
      A001: [{ size: "L", color: "Đỏ", qty_on_hand: 2, status: "reserved" }],
    });
    const padded = await getOnHandRows("A01");
    assert.equal(padded.length, 1);
    assert.equal(padded[0].size, "L");
    assert.equal(padded[0].qty_on_hand, 2);

    writeOnHand({
      A01: [{ size: "M", color: "Kem", qty_on_hand: 1, status: "on_hand" }],
      a01: [{ size: "S", color: "Đen", qty_on_hand: 4, status: "sold" }],
    });
    const canonical = await getOnHandRows("A1");
    assert.equal(canonical.length, 1);
    assert.equal(canonical[0].size, "M");
    assert.equal(canonical[0].qty_on_hand, 1);
  });
});

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

function writeOnHand(onHand: Record<string, unknown>): void {
  const file = path.join(process.env.SASSY_DATA_DIR ?? "", "submissions.json");
  const disk = JSON.parse(fs.readFileSync(file, "utf8")) as { on_hand?: unknown };
  disk.on_hand = onHand;
  fs.writeFileSync(file, JSON.stringify(disk));
  resetStoreBackendForTests();
}
