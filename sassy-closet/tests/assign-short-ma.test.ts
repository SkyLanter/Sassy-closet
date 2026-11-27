import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";
import { hashBytes, listSubmissions, saveSubmission } from "../lib/store";
import { resetStoreBackendForTests } from "../lib/store-backend";
import type { SaveInput } from "../lib/store";

const ENV_KEYS = [
  "SASSY_DATA_DIR",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
  "NEW_MA_WEBHOOK_URL",
  "NEW_MA_WEBHOOK_TOKEN",
] as const;

const prev: Record<string, string | undefined> = {};
let tmp = "";

afterEach(() => {
  for (const key of ENV_KEYS) {
    if (prev[key] === undefined) delete process.env[key];
    else process.env[key] = prev[key];
  }
  resetStoreBackendForTests();
  if (tmp) fs.rmSync(tmp, { recursive: true, force: true });
  tmp = "";
});

function useTempStore(): void {
  for (const key of ENV_KEYS) {
    if (!(key in prev)) prev[key] = process.env[key];
    delete process.env[key];
  }
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-short-ma-"));
  process.env.SASSY_DATA_DIR = tmp;
  resetStoreBackendForTests();
}

function blankSave(overrides: { kind?: string; newMa?: string; sellUsd?: string } = {}): SaveInput {
  const bytes = Buffer.from("photo");
  return {
    kind: overrides.kind ?? "Q",
    size: "S",
    link: "",
    color: "",
    color_note: "",
    pieces: [],
    cost_usd: "",
    cost_cny: "80",
    cost_currency: "CNY",
    sell_usd: overrides.sellUsd ?? "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: [],
    photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    newMa: overrides.newMa,
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
  };
}

test("a one-digit new mã is the canonical code, including Q02", async () => {
  useTempStore();
  const queen = await saveSubmission(blankSave({ kind: "Q", newMa: "Q2" }));
  assert.equal(queen.ma, "Q02");
  assert.equal(queen.kind, "Q");
  await assert.rejects(() => saveSubmission(blankSave({ kind: "Q", newMa: "q2" })), /đã có rồi/);
  const letter = await saveSubmission(blankSave({ kind: "A", newMa: "A" }));
  assert.equal(letter.ma, "A01");
  const rows = await listSubmissions();
  assert.deepEqual(rows.map((row) => row.ma), ["Q02", "A01"]);
});

test("a one-digit held mã and a one-digit S06 still hit the existing blocks", async () => {
  useTempStore();
  await assert.rejects(() => saveSubmission(blankSave({ kind: "K", newMa: "K6" })), /held/);
  await assert.rejects(
    () => saveSubmission(blankSave({ kind: "S", newMa: "s6", sellUsd: "30" })),
    /s06-lock/,
  );
  assert.deepEqual(await listSubmissions(), []);
  const locked = await saveSubmission(blankSave({ kind: "S", newMa: "s6", sellUsd: "25" }));
  assert.equal(locked.ma, "S06");
  assert.equal(locked.sell_usd, "25");
});

test("a letter still mints the next mã and junk is still rejected", async () => {
  useTempStore();
  const minted = await saveSubmission(blankSave({ kind: "Q", newMa: "Q" }));
  assert.equal(minted.ma, "Q01");
  await assert.rejects(() => saveSubmission(blankSave({ kind: "Q", newMa: "QQ" })), /Mã mới/);
});
