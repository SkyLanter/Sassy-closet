import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import {
  buildIntakeDatasetSyncPayload,
  intakeDatasetSyncWebhookConfigured,
  notifyIntakeDatasetSyncWebhook,
} from "../lib/intakeDatasetSyncWebhook";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { hashBytes, saveSubmission } from "../lib/store";
import type { Submission } from "../lib/types";

const ENV_KEYS = [
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
] as const;

const STORE_ENV_KEYS = [
  "SASSY_DATA_DIR",
  "VERCEL",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "BLOB_ACCESS",
] as const;

const TEST_URL = "https://example.invalid/intake-dataset-sync";
const TEST_KEY = "test-sender-key";

describe("intake dataset sync webhook helper", () => {
  const prev: Record<string, string | undefined> = {};
  let fetchCalls: { url: string; init: RequestInit }[] = [];
  let originalFetch: typeof fetch | undefined;
  let errors: unknown[][] = [];
  let originalError: typeof console.error;

  beforeEach(() => {
    for (const key of ENV_KEYS) {
      prev[key] = process.env[key];
      delete process.env[key];
    }
    fetchCalls = [];
    originalFetch = globalThis.fetch;
    globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
      fetchCalls.push({ url: String(input), init: init ?? {} });
      return new Response(null, { status: 204 });
    }) as typeof fetch;
    errors = [];
    originalError = console.error;
    console.error = (...args: unknown[]) => {
      errors.push(args);
    };
  });

  afterEach(() => {
    for (const key of ENV_KEYS) {
      if (prev[key] === undefined) delete process.env[key];
      else process.env[key] = prev[key];
    }
    if (originalFetch) globalThis.fetch = originalFetch;
    console.error = originalError;
  });

  test("payload maps stored fields and omits blanks — never invents values", () => {
    const full = buildIntakeDatasetSyncPayload("create", stagedItem());
    assert.equal(full.event, "create");
    assert.equal(full.ma, "A01");
    assert.equal(full.source, "intake");
    assert.equal(full.timestamp, "2026-09-10T17:00:00.000Z");
    assert.deepEqual(full.sizes, ["M", "L"]);
    assert.deepEqual(full.colors, ["Kem", "Xanh"]);
    assert.equal(full.cost, "12");
    assert.equal(full.sell, "28");
    assert.equal(full.source_link, "https://e.tb.cn/example");
    assert.equal(full.kind, "A");
    assert.equal(full.photo_count, 1);

    const blank = buildIntakeDatasetSyncPayload(
      "update",
      stagedItem({
        size: "  ",
        color: "",
        pieces: [{ id: "p1", photos: [], suggested: ["ignore-me"], color: "", note: "" }],
        link: "",
        price: "",
        cost_cny: "",
        cost_usd: "",
        sell_cny: "",
        sell_usd: "",
        photo_paths: [],
      }),
    );
    assert.equal(blank.event, "update");
    assert.equal(blank.ma, "A01");
    assert.equal("sizes" in blank, false);
    assert.equal("colors" in blank, false);
    assert.equal("cost" in blank, false);
    assert.equal("sell" in blank, false);
    assert.equal("source_link" in blank, false);
    assert.equal("photo_count" in blank, false);
    assert.ok(!JSON.stringify(blank).includes("ignore-me"));
  });

  test("CNY cost/sell use the stored CNY amount when that currency is set", () => {
    const payload = buildIntakeDatasetSyncPayload(
      "create",
      stagedItem({
        cost_currency: "CNY",
        cost_cny: "80.52",
        cost_usd: "12",
        sell_currency: "CNY",
        sell_cny: "188",
        sell_usd: "",
        price: "",
      }),
    );
    assert.equal(payload.cost, "80.52");
    assert.equal(payload.sell, "188");
  });

  test("piece color is included only when already on the record", () => {
    const payload = buildIntakeDatasetSyncPayload(
      "update",
      stagedItem({
        color: "Kem",
        pieces: [{ id: "p1", photos: [], suggested: ["Đỏ"], color: "Xanh mint", note: "" }],
      }),
    );
    assert.deepEqual(payload.colors, ["Kem", "Xanh mint"]);
    assert.ok(!payload.colors?.includes("Đỏ"));
  });

  test("unset or partial env is a no-op — fetch is not called", async () => {
    assert.equal(intakeDatasetSyncWebhookConfigured(), false);
    await notifyIntakeDatasetSyncWebhook("create", stagedItem());
    assert.equal(fetchCalls.length, 0);

    process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = TEST_URL;
    assert.equal(intakeDatasetSyncWebhookConfigured(), false);
    await notifyIntakeDatasetSyncWebhook("create", stagedItem());
    assert.equal(fetchCalls.length, 0);

    delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL;
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = TEST_KEY;
    assert.equal(intakeDatasetSyncWebhookConfigured(), false);
    await notifyIntakeDatasetSyncWebhook("update", stagedItem());
    assert.equal(fetchCalls.length, 0);
  });

  test("configured POST sends Bearer + X-Automation-Key and does not log the key", async () => {
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = TEST_URL;
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = TEST_KEY;
    assert.equal(intakeDatasetSyncWebhookConfigured(), true);

    await notifyIntakeDatasetSyncWebhook("create", stagedItem());
    assert.equal(fetchCalls.length, 1);
    assert.equal(fetchCalls[0].url, TEST_URL);
    const headers = new Headers(fetchCalls[0].init.headers);
    assert.equal(headers.get("content-type"), "application/json");
    assert.equal(headers.get("authorization"), `Bearer ${TEST_KEY}`);
    assert.equal(headers.get("x-automation-key"), TEST_KEY);
    const body = JSON.parse(String(fetchCalls[0].init.body)) as { event: string; ma: string };
    assert.equal(body.event, "create");
    assert.equal(body.ma, "A01");
    assert.equal(errors.length, 0);
    assertNoSecret(errors);
  });

  test("HTTP 5xx is logged without the key and does not throw", async () => {
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = TEST_URL;
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = TEST_KEY;
    globalThis.fetch = (async () => new Response("nope", { status: 503 })) as typeof fetch;

    await notifyIntakeDatasetSyncWebhook("update", stagedItem({ ma: "Q01" }));
    assert.equal(errors.length, 1);
    assert.deepEqual(errors[0][0], "[intake-dataset-sync-webhook]");
    assert.deepEqual(errors[0][1], { event: "update", ma: "Q01", status: 503 });
    assertNoSecret(errors);
  });

  test("network / timeout errors are soft", async () => {
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = TEST_URL;
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = TEST_KEY;
    globalThis.fetch = (async () => {
      const err = new DOMException("The operation was aborted.", "TimeoutError");
      throw err;
    }) as typeof fetch;

    await notifyIntakeDatasetSyncWebhook("create", stagedItem());
    assert.equal(errors.length, 1);
    assert.deepEqual(errors[0][1], { event: "create", ma: "A01", status: "timeout" });
    assertNoSecret(errors);
  });
});

describe("saveSubmission fires dataset sync after persist", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};
  let fetchCalls: { url: string; init: RequestInit }[] = [];
  let originalFetch: typeof fetch | undefined;

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-sync-"));
    for (const key of [...STORE_ENV_KEYS, ...ENV_KEYS]) {
      prev[key] = process.env[key];
      delete process.env[key];
    }
    process.env.SASSY_DATA_DIR = tmp;
    resetStoreBackendForTests();
    fetchCalls = [];
    originalFetch = globalThis.fetch;
    globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
      fetchCalls.push({ url: String(input), init: init ?? {} });
      return new Response(null, { status: 204 });
    }) as typeof fetch;
  });

  afterEach(() => {
    for (const [key, value] of Object.entries(prev)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
    if (originalFetch) globalThis.fetch = originalFetch;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("create and update each POST once with the persisted mã", async () => {
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = TEST_URL;
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = TEST_KEY;

    const created = await saveSubmission(blankSave({ color: "Kem", size: "M" }));
    assert.equal(created.ma, "A01");
    assert.equal(fetchCalls.length, 1);
    const createdBody = JSON.parse(String(fetchCalls[0].init.body)) as {
      event: string;
      ma: string;
      sizes: string[];
      colors: string[];
    };
    assert.equal(createdBody.event, "create");
    assert.equal(createdBody.ma, "A01");
    assert.deepEqual(createdBody.sizes, ["M"]);
    assert.deepEqual(createdBody.colors, ["Kem"]);

    const updated = await saveSubmission(
      blankSave({ color: "Đen", size: "L", existingMa: created.ma }),
    );
    assert.equal(updated.ma, "A01");
    assert.equal(updated.color, "Đen");
    assert.equal(fetchCalls.length, 2);
    const updatedBody = JSON.parse(String(fetchCalls[1].init.body)) as {
      event: string;
      ma: string;
    };
    assert.equal(updatedBody.event, "update");
    assert.equal(updatedBody.ma, "A01");
  });

  test("unset env does not call fetch; save still persists", async () => {
    const saved = await saveSubmission(blankSave({ color: "Trắng" }));
    assert.equal(saved.ma, "A01");
    assert.equal(fetchCalls.length, 0);
    const disk = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
      submissions: { ma: string }[];
    };
    assert.equal(disk.submissions[0].ma, "A01");
  });

  test("webhook 4xx does not roll back the save", async () => {
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = TEST_URL;
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = TEST_KEY;
    globalThis.fetch = (async () => new Response("bad", { status: 401 })) as typeof fetch;

    const saved = await saveSubmission(blankSave({ color: "Be" }));
    assert.equal(saved.ma, "A01");
    const disk = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
      submissions: { ma: string; color: string }[];
    };
    assert.equal(disk.submissions[0].color, "Be");
  });

  test("webhook throw does not roll back the save", async () => {
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL = TEST_URL;
    process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY = TEST_KEY;
    globalThis.fetch = (async () => {
      throw new Error("ECONNREFUSED");
    }) as typeof fetch;

    const saved = await saveSubmission(blankSave({ color: "Hồng" }));
    assert.equal(saved.ma, "A01");
  });
});

function stagedItem(overrides: Partial<Submission> = {}): Submission {
  return {
    id: 1,
    ma: "A01",
    kind: "A",
    size: "M L",
    color: "Kem, Xanh",
    color_note: "",
    pieces: [],
    link: "https://e.tb.cn/example",
    price: "28",
    cost_cny: "",
    cost_usd: "12",
    cost_currency: "USD",
    sell_cny: "",
    sell_usd: "28",
    sell_currency: "USD",
    blurb: "",
    photo_paths: ["A01/001.jpg"],
    photo_hashes: ["abc"],
    status: "staged",
    square: "not_square",
    created_at: "2026-09-10T17:00:00.000Z",
    updated_at: "2026-09-10T17:00:00.000Z",
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: "Documents/Sassy Closet/Photos/A01/",
    ...overrides,
  };
}

function blankSave(overrides: { color?: string; size?: string; existingMa?: string } = {}) {
  const bytes = Buffer.from(`photo-${overrides.color ?? "x"}`);
  return {
    kind: "A",
    size: overrides.size ?? "",
    link: "",
    color: overrides.color ?? "",
    color_note: "",
    pieces: [],
    cost_usd: "",
    cost_cny: "",
    cost_currency: "USD",
    sell_usd: "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: [] as string[],
    photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    existingMa: overrides.existingMa,
  };
}

function assertNoSecret(logs: unknown[][]): void {
  const dumped = JSON.stringify(logs);
  assert.ok(!dumped.includes(TEST_KEY));
  assert.ok(!dumped.includes("Bearer "));
  assert.ok(!dumped.includes("Authorization"));
}
