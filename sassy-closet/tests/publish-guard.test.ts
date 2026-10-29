import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";
import {
  buildIntakeDatasetSyncPayload,
  notifyIntakeDatasetSyncWebhook,
} from "../lib/intakeDatasetSyncWebhook";
import { notifyNewMaWebhook } from "../lib/newMaWebhook";
import { nextMa } from "../lib/mint";
import { mintBlock, publishBlock } from "../lib/publish-guard";
import { hashBytes, listSubmissions, saveSubmission } from "../lib/store";
import { resetStoreBackendForTests } from "../lib/store-backend";
import type { Submission } from "../lib/types";

const ENV_KEYS = [
  "SASSY_DATA_DIR",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
  "NEW_MA_WEBHOOK_URL",
  "NEW_MA_WEBHOOK_TOKEN",
] as const;

const prev: Record<string, string | undefined> = {};

afterEach(() => {
  for (const key of ENV_KEYS) {
    if (prev[key] === undefined) delete process.env[key];
    else process.env[key] = prev[key];
  }
  resetStoreBackendForTests();
});

test("publish guard allows Q02 and still blocks held mãs, a reused mã, and S06 off $25", () => {
  assert.equal(publishBlock({ action: "create", ma: "Q02" }), null);
  assert.equal(publishBlock({ action: "sync", ma: "q02", sellUsd: "20" }), null);
  assert.equal(publishBlock({ action: "mint", ma: "Q02" }), null);
  assert.equal(publishBlock({ action: "create", ma: "K06" }), "held");
  assert.equal(publishBlock({ action: "sync", ma: "V05" }), "held");
  assert.equal(publishBlock({ action: "create", ma: "A01", reused: true }), "reused");
  assert.equal(publishBlock({ action: "create", ma: "A01", duplicate: true }), "duplicate");
  assert.equal(publishBlock({ action: "update", ma: "S06", sellUsd: "30" }), "s06-lock");
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "$24" }), "s06-lock");
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "25.50" }), "s06-lock");
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "25" }), null);
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "25.00" }), null);
  assert.equal(publishBlock({ action: "update", ma: "S06", sellUsd: "" }), null);
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "40" }), "s06-lock");
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "25", sellCurrency: "CNY" }), "s06-lock");
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "180", sellCurrency: "cny" }), "s06-lock");
  assert.equal(mintBlock("K", ["K01", "K02", "K03", "K04", "K05"]), "held");
  assert.equal(mintBlock("Q", ["Q01"]), null);
  assert.equal(mintBlock("A", []), null);
});

test("holding G01 refuses that shoe and the next code is G02 once G01 exists", () => {
  assert.equal(nextMa("G", []), "G01");
  assert.equal(mintBlock("G", []), "held");
  assert.equal(publishBlock({ action: "create", ma: "G01" }), "held");
  assert.equal(publishBlock({ action: "update", ma: "G01" }), "held");
  assert.equal(nextMa("G", ["G01"]), "G02");
  assert.equal(mintBlock("G", ["G01"]), null);
  assert.equal(publishBlock({ action: "create", ma: "G02" }), null);
});

test("holding H02 and A29 blocks those codes and leaves the following number free", () => {
  assert.equal(nextMa("H", ["H01"]), "H02");
  assert.equal(mintBlock("H", ["H01"]), "held");
  assert.equal(nextMa("H", ["H01", "H02"]), "H03");
  assert.equal(mintBlock("H", ["H01", "H02"]), null);
  const throughA28 = Array.from({ length: 28 }, (_, index) => `A${String(index + 1).padStart(2, "0")}`);
  assert.equal(nextMa("A", throughA28), "A29");
  assert.equal(mintBlock("A", throughA28), "held");
  assert.equal(nextMa("A", [...throughA28, "A29"]), "A30");
  assert.equal(mintBlock("A", [...throughA28, "A29"]), null);
  assert.equal(publishBlock({ action: "create", ma: "S16" }), "held");
  assert.equal(publishBlock({ action: "create", ma: "S19" }), "held");
});

test("save persists Q02 and still refuses K06 or S06 at another dollar", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-guard-"));
  rememberEnv();
  process.env.SASSY_DATA_DIR = tmp;
  delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL;
  delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY;
  resetStoreBackendForTests();
  const queen = await saveSubmission(blankSave({ kind: "Q", newMa: "Q02" }));
  assert.equal(queen.ma, "Q02");
  assert.equal(queen.status, "staged");
  assert.equal(queen.square, "not_square");
  await assert.rejects(() => saveSubmission(blankSave({ kind: "Q", newMa: "q02" })), /đã có rồi/);
  await assert.rejects(() => saveSubmission(blankSave({ kind: "K", newMa: "K06" })), /held/);
  await assert.rejects(() => saveSubmission(blankSave({ kind: "S", newMa: "S06", sellUsd: "30" })), /s06-lock/);
  const locked = await saveSubmission(blankSave({ kind: "S", newMa: "S06", sellUsd: "25" }));
  assert.equal(locked.ma, "S06");
  assert.equal(locked.sell_usd, "25");
  await assert.rejects(
    () => saveSubmission(blankSave({ kind: "S", existingMa: "S06", sellUsd: "40" })),
    /s06-lock/,
  );
  const rows = await listSubmissions();
  assert.deepEqual(rows.map((row) => row.ma), ["Q02", "S06"]);
  assert.equal(rows[0]?.status, "staged");
  assert.equal(rows[1]?.sell_usd, "25");
  fs.rmSync(tmp, { recursive: true, force: true });
});

test("mint through save assigns Q02 and does not emit K06", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-mint-"));
  rememberEnv();
  process.env.SASSY_DATA_DIR = tmp;
  delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL;
  delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY;
  resetStoreBackendForTests();
  const seeded = ["K01", "K02", "K03", "K04", "K05", "Q01"].map((ma, index) => ({ ma, id: index + 1 }));
  fs.writeFileSync(
    path.join(tmp, "submissions.json"),
    JSON.stringify({ nextId: 7, submissions: seeded, fx: { usd_cny: 6.71, updated: "2026-09-07" } }),
  );
  await assert.rejects(() => saveSubmission(blankSave({ kind: "K", newMa: "K" })), /K06/);
  const minted = await saveSubmission(blankSave({ kind: "Q", newMa: "Q" }));
  assert.equal(minted.ma, "Q02");
  assert.equal(minted.status, "staged");
  assert.equal(minted.square, "not_square");
  const rows = await listSubmissions();
  assert.deepEqual(
    rows.map((row) => row.ma),
    [...seeded.map((row) => row.ma), "Q02"],
  );
  fs.rmSync(tmp, { recursive: true, force: true });
});

test("dataset sync and new-mã webhook do not post blocked mãs", async () => {
  rememberEnv();
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = "https://example.invalid/intake-dataset-sync";
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = "test-sender-key";
  process.env.NEW_MA_WEBHOOK_URL = "https://example.invalid/new-ma";
  process.env.NEW_MA_WEBHOOK_TOKEN = "test-token";
  const calls: string[] = [];
  const original = globalThis.fetch;
  globalThis.fetch = (async (url: string | URL | Request) => {
    calls.push(String(url));
    return new Response("ok", { status: 200 });
  }) as typeof fetch;
  try {
    await notifyIntakeDatasetSyncWebhook("create", submission({ ma: "Q02", kind: "Q" }));
    await notifyIntakeDatasetSyncWebhook("create", submission({ ma: "K06", kind: "K" }));
    await notifyIntakeDatasetSyncWebhook("update", submission({ ma: "S06", kind: "S", sell_usd: "30", price: "30" }));
    await notifyIntakeDatasetSyncWebhook("update", submission({ ma: "S06", kind: "S", sell_usd: "25", price: "25" }));
    await notifyNewMaWebhook({
      event: "create",
      ma: "Q02",
      updated_at: "2026-10-11T00:00:00.000Z",
      photo_count: 1,
    });
    await notifyNewMaWebhook({
      event: "create",
      ma: "K06",
      updated_at: "2026-10-11T00:00:00.000Z",
      photo_count: 1,
    });
    await notifyNewMaWebhook({
      event: "create",
      ma: "A08",
      updated_at: "2026-10-11T00:00:00.000Z",
      photo_count: 1,
    });
  } finally {
    globalThis.fetch = original;
  }
  assert.deepEqual(calls, [
    "https://example.invalid/intake-dataset-sync",
    "https://example.invalid/intake-dataset-sync",
    "https://example.invalid/new-ma",
    "https://example.invalid/new-ma",
  ]);
});

test("next mã skips a fake never-list gap and a number that already exists", () => {
  assert.equal(nextMa("P", ["P01"], ["P02"]), "P03");
  assert.equal(nextMa("P", ["P01"], ["P02", "P03"]), "P04");
  assert.equal(nextMa("P", ["P01", "P04"], ["P02", "P03"]), "P05");
  assert.equal(nextMa("Q", ["Q01"]), "Q02");
});

test("sync refuses S06 when the posted sell is not the $25 dollar", async () => {
  const calls: { url: string; body: string }[] = [];
  await withSyncFetch(calls, async () => {
    await notifyIntakeDatasetSyncWebhook(
      "update",
      submission({ ma: "S06", kind: "S", sell_usd: "", sell_cny: "", sell_currency: "USD", price: "40" }),
    );
    await notifyIntakeDatasetSyncWebhook(
      "create",
      submission({
        ma: "S06",
        kind: "S",
        sell_usd: "25",
        sell_cny: "180",
        sell_currency: "CNY",
        price: "25",
      }),
    );
  });
  assert.deepEqual(calls, []);
  const priced = buildIntakeDatasetSyncPayload(
    "create",
    submission({ ma: "S06", kind: "S", sell_usd: "", price: "40" }),
  );
  assert.equal(priced.sell, "40");
  const yuan = buildIntakeDatasetSyncPayload(
    "create",
    submission({ ma: "S06", kind: "S", sell_usd: "25", sell_cny: "180", sell_currency: "CNY", price: "25" }),
  );
  assert.equal(yuan.sell, "180");
});

test("an already-listed mã does not sync a new sell", async () => {
  const listed = submission({ ma: "A01", sell_usd: "30", price: "30" });
  const edited = submission({ ma: "A01", sell_usd: "99", price: "99" });
  const payload = buildIntakeDatasetSyncPayload("update", edited);
  assert.equal("sell" in payload, false);
  const calls: { url: string; body: string }[] = [];
  await withSyncFetch(calls, async () => {
    await notifyIntakeDatasetSyncWebhook("update", edited, listed);
  });
  assert.deepEqual(calls, []);
});

test("save refuses an S06 CNY sell and does not post it", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-s06-cny-"));
  rememberEnv();
  process.env.SASSY_DATA_DIR = tmp;
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = "https://example.invalid/intake-dataset-sync";
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = "test-sender-key";
  resetStoreBackendForTests();
  const calls: string[] = [];
  const original = globalThis.fetch;
  globalThis.fetch = (async (url: string | URL | Request) => {
    calls.push(String(url));
    return new Response("ok", { status: 200 });
  }) as typeof fetch;
  try {
    const locked = await saveSubmission(blankSave({ kind: "S", newMa: "S06", sellUsd: "25" }));
    assert.equal(locked.sell_usd, "25");
    await assert.rejects(
      () =>
        saveSubmission(
          blankSave({
            kind: "S",
            existingMa: "S06",
            sellUsd: "25",
            sellCny: "180",
            sellCurrency: "CNY",
          }),
        ),
      /s06-lock/,
    );
  } finally {
    globalThis.fetch = original;
  }
  const rows = await listSubmissions();
  assert.equal(rows.length, 1);
  assert.equal(rows[0]?.sell_usd, "25");
  assert.equal(rows[0]?.sell_currency, "USD");
  assert.deepEqual(calls, ["https://example.invalid/intake-dataset-sync"]);
  fs.rmSync(tmp, { recursive: true, force: true });
});

test("editing a listed mã keeps the new sell off the dataset sync", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-listed-edit-"));
  rememberEnv();
  process.env.SASSY_DATA_DIR = tmp;
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = "https://example.invalid/intake-dataset-sync";
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = "test-sender-key";
  resetStoreBackendForTests();
  const bodies: string[] = [];
  const original = globalThis.fetch;
  globalThis.fetch = (async (_url: string | URL | Request, init?: RequestInit) => {
    bodies.push(String(init?.body ?? ""));
    return new Response("ok", { status: 200 });
  }) as typeof fetch;
  try {
    await saveSubmission(blankSave({ kind: "A", newMa: "A01", sellUsd: "30" }));
    const edited = await saveSubmission(
      blankSave({ kind: "A", existingMa: "A01", sellUsd: "99", color: "Đen" }),
    );
    assert.equal(edited.sell_usd, "99");
    assert.equal(edited.color, "Đen");
  } finally {
    globalThis.fetch = original;
  }
  assert.equal(bodies.length, 1);
  assert.equal(JSON.parse(bodies[0] ?? "{}").sell, "30");
  assert.equal(bodies.some((body) => body.includes('"99"')), false);
  fs.rmSync(tmp, { recursive: true, force: true });
});

test("a duplicate mã is not saved and is not synced", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-dup-"));
  rememberEnv();
  process.env.SASSY_DATA_DIR = tmp;
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = "https://example.invalid/intake-dataset-sync";
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = "test-sender-key";
  resetStoreBackendForTests();
  const calls: string[] = [];
  const original = globalThis.fetch;
  globalThis.fetch = (async (url: string | URL | Request) => {
    calls.push(String(url));
    return new Response("ok", { status: 200 });
  }) as typeof fetch;
  try {
    await saveSubmission(blankSave({ kind: "A", newMa: "A01", sellUsd: "28" }));
    await assert.rejects(() => saveSubmission(blankSave({ kind: "A", newMa: "a01", sellUsd: "99" })), /đã có rồi/);
  } finally {
    globalThis.fetch = original;
  }
  const rows = await listSubmissions();
  assert.deepEqual(rows.map((row) => row.ma), ["A01"]);
  assert.equal(rows[0]?.sell_usd, "28");
  assert.deepEqual(calls, ["https://example.invalid/intake-dataset-sync"]);
  fs.rmSync(tmp, { recursive: true, force: true });
});

function rememberEnv(): void {
  for (const key of ENV_KEYS) prev[key] = process.env[key];
}

async function withSyncFetch(
  calls: { url: string; body: string }[],
  run: () => Promise<void>,
): Promise<void> {
  rememberEnv();
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = "https://example.invalid/intake-dataset-sync";
  process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = "test-sender-key";
  const original = globalThis.fetch;
  globalThis.fetch = (async (url: string | URL | Request, init?: RequestInit) => {
    calls.push({ url: String(url), body: String(init?.body ?? "") });
    return new Response("ok", { status: 200 });
  }) as typeof fetch;
  try {
    await run();
  } finally {
    globalThis.fetch = original;
  }
}

function blankSave(
  overrides: {
    kind?: string;
    newMa?: string;
    existingMa?: string;
    sellUsd?: string;
    sellCny?: string;
    sellCurrency?: string;
    color?: string;
  } = {},
) {
  const bytes = Buffer.from("photo");
  return {
    kind: overrides.kind ?? "A",
    size: "S",
    link: "",
    color: overrides.color ?? "",
    color_note: "",
    pieces: [],
    cost_usd: "",
    cost_cny: "80",
    cost_currency: "CNY",
    sell_usd: overrides.sellUsd ?? "",
    sell_cny: overrides.sellCny ?? "",
    sell_currency: overrides.sellCurrency ?? "USD",
    keep_photos: [] as string[],
    photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    existingMa: overrides.existingMa,
    newMa: overrides.newMa,
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
  };
}

function submission(overrides: Partial<Submission>): Submission {
  return {
    id: 1,
    ma: "A01",
    kind: "A",
    size: "S",
    color: "",
    color_note: "",
    pieces: [],
    link: "",
    price: "28",
    cost_cny: "80",
    cost_usd: "",
    cost_currency: "CNY",
    sell_cny: "",
    sell_usd: "28",
    sell_currency: "USD",
    blurb: "",
    photo_paths: [],
    photo_hashes: [],
    status: "staged",
    square: "not_square",
    created_at: "2026-10-11T00:00:00.000Z",
    updated_at: "2026-10-11T00:00:00.000Z",
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: "",
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    ...overrides,
  };
}
