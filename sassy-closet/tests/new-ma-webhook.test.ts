import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { POST } from "../app/api/submissions/route";
import { PATCH } from "../app/api/submissions/[ma]/route";
import {
  buildNewMaWebhookPayload,
  newMaWebhookConfigured,
  newMaWebhookUrlConfigured,
  notifyNewMaWebhook,
  scheduleNewMaWebhook,
  type NewMaWebhookInput,
} from "../lib/newMaWebhook";
import { resetStoreBackendForTests } from "../lib/store-backend";

const ENV_KEYS = ["NEW_MA_WEBHOOK_URL", "NEW_MA_WEBHOOK_TOKEN"] as const;

const STORE_ENV_KEYS = [
  "SASSY_DATA_DIR",
  "VERCEL",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "BLOB_ACCESS",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
] as const;

const TEST_URL = "https://example.invalid/new-ma";
const TEST_TOKEN = "test-new-ma-token";

describe("new mã webhook helper", () => {
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

  test("payload is only the saved mã fields — nothing invented", () => {
    const payload = buildNewMaWebhookPayload(sampleInput());
    assert.deepEqual(payload, {
      event: "create",
      ma: "A17",
      updated_at: "2026-09-28T08:12:10.000Z",
      source: "intake",
      photo_count: 2,
    });
    const blank = buildNewMaWebhookPayload(sampleInput({ event: "update", photo_count: 0 }));
    assert.equal(blank.photo_count, 0);
    assert.equal("photo_count" in blank, true);
  });

  test("unset, whitespace, or half-set env is a no-op — fetch is not called", async () => {
    assert.equal(newMaWebhookConfigured(), false);
    assert.equal(newMaWebhookUrlConfigured(), false);
    await notifyNewMaWebhook(sampleInput());
    assert.equal(fetchCalls.length, 0);

    process.env.NEW_MA_WEBHOOK_URL = "  ";
    process.env.NEW_MA_WEBHOOK_TOKEN = TEST_TOKEN;
    assert.equal(newMaWebhookConfigured(), false);
    assert.equal(newMaWebhookUrlConfigured(), false);
    await notifyNewMaWebhook(sampleInput());
    assert.equal(fetchCalls.length, 0);

    process.env.NEW_MA_WEBHOOK_URL = TEST_URL;
    delete process.env.NEW_MA_WEBHOOK_TOKEN;
    assert.equal(newMaWebhookConfigured(), false);
    assert.equal(newMaWebhookUrlConfigured(), true);
    await notifyNewMaWebhook(sampleInput());
    assert.equal(fetchCalls.length, 0);

    delete process.env.NEW_MA_WEBHOOK_URL;
    process.env.NEW_MA_WEBHOOK_TOKEN = `  ${TEST_TOKEN}  `;
    assert.equal(newMaWebhookConfigured(), false);
    await notifyNewMaWebhook(sampleInput({ event: "update" }));
    assert.equal(fetchCalls.length, 0);
  });

  test("configured POST sends Bearer + X-Automation-Key and the saved payload", async () => {
    process.env.NEW_MA_WEBHOOK_URL = `  ${TEST_URL}  `;
    process.env.NEW_MA_WEBHOOK_TOKEN = `  ${TEST_TOKEN}  `;
    assert.equal(newMaWebhookConfigured(), true);

    await notifyNewMaWebhook(sampleInput());
    assert.equal(fetchCalls.length, 1);
    assert.equal(fetchCalls[0].url, TEST_URL);
    assert.equal(fetchCalls[0].init.method, "POST");
    assert.equal(fetchCalls[0].init.redirect, "manual");
    const headers = new Headers(fetchCalls[0].init.headers);
    assert.equal(headers.get("content-type"), "application/json");
    assert.equal(headers.get("authorization"), `Bearer ${TEST_TOKEN}`);
    assert.equal(headers.get("x-automation-key"), TEST_TOKEN);
    assert.ok(fetchCalls[0].init.signal instanceof AbortSignal);
    assert.deepEqual(JSON.parse(String(fetchCalls[0].init.body)), {
      event: "create",
      ma: "A17",
      updated_at: "2026-09-28T08:12:10.000Z",
      source: "intake",
      photo_count: 2,
    });
    assert.equal(errors.length, 0);
    assertNoSecret(errors);
  });

  test("HTTP 500 is logged as the status code and does not throw", async () => {
    process.env.NEW_MA_WEBHOOK_URL = TEST_URL;
    process.env.NEW_MA_WEBHOOK_TOKEN = TEST_TOKEN;
    globalThis.fetch = (async () => new Response("nope", { status: 500 })) as typeof fetch;

    await notifyNewMaWebhook(sampleInput({ event: "update", ma: "A22" }));
    assert.equal(errors.length, 1);
    assert.deepEqual(errors[0][0], "[new-ma-webhook]");
    assert.deepEqual(errors[0][1], { event: "update", ma: "A22", status: 500 });
    assertNoSecret(errors);
  });

  test("timeout and network errors resolve without throwing", async () => {
    process.env.NEW_MA_WEBHOOK_URL = TEST_URL;
    process.env.NEW_MA_WEBHOOK_TOKEN = TEST_TOKEN;
    globalThis.fetch = (async () => {
      throw new DOMException("The operation was aborted.", "TimeoutError");
    }) as typeof fetch;

    await notifyNewMaWebhook(sampleInput());
    assert.deepEqual(errors[0][1], { event: "create", ma: "A17", status: "timeout" });

    errors.length = 0;
    globalThis.fetch = (async () => {
      throw new Error(`connect ${TEST_URL} failed bearer ${TEST_TOKEN}`);
    }) as typeof fetch;
    await notifyNewMaWebhook(sampleInput({ event: "update" }));
    assert.deepEqual(errors[0][1], { event: "update", ma: "A17", status: "network" });
    assertNoSecret(errors);
  });

  test("schedule outside a request still sends and does not throw", async () => {
    process.env.NEW_MA_WEBHOOK_URL = TEST_URL;
    process.env.NEW_MA_WEBHOOK_TOKEN = TEST_TOKEN;
    scheduleNewMaWebhook(sampleInput({ ma: "S13" }));
    await flush();
    assert.equal(fetchCalls.length, 1);
    const body = JSON.parse(String(fetchCalls[0].init.body)) as { ma: string; event: string };
    assert.equal(body.ma, "S13");
    assert.equal(body.event, "create");
  });
});

describe("save routes stay 200 when the new-mã webhook fails", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};
  let fetchCalls: { url: string; init: RequestInit }[] = [];
  let originalFetch: typeof fetch | undefined;
  let errors: unknown[][] = [];
  let originalError: typeof console.error;

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-new-ma-"));
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
    errors = [];
    originalError = console.error;
    console.error = (...args: unknown[]) => {
      errors.push(args);
    };
  });

  afterEach(() => {
    for (const [key, value] of Object.entries(prev)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
    if (originalFetch) globalThis.fetch = originalFetch;
    console.error = originalError;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("create and rename update POST the persisted mã", async () => {
    process.env.NEW_MA_WEBHOOK_URL = TEST_URL;
    process.env.NEW_MA_WEBHOOK_TOKEN = TEST_TOKEN;

    const createdRes = await POST(jsonForm("POST", "/api/submissions"));
    assert.equal(createdRes.status, 200);
    const created = (await createdRes.json()) as { submission: { ma: string; updated_at: string } };
    await flush();
    assert.equal(created.submission.ma, "A01");
    assert.equal(fetchCalls.length, 1);
    const createdBody = JSON.parse(String(fetchCalls[0].init.body)) as {
      event: string;
      ma: string;
      updated_at: string;
      photo_count: number;
    };
    assert.equal(createdBody.event, "create");
    assert.equal(createdBody.ma, "A01");
    assert.equal(createdBody.updated_at, created.submission.updated_at);
    assert.equal(createdBody.photo_count, 0);

    const patchedRes = await PATCH(jsonForm("PATCH", "/api/submissions/A01", { new_ma: "A09" }), {
      params: Promise.resolve({ ma: "A01" }),
    });
    assert.equal(patchedRes.status, 200);
    const patched = (await patchedRes.json()) as { submission: { ma: string; updated_at: string } };
    await flush();
    assert.equal(patched.submission.ma, "A09");
    assert.equal(fetchCalls.length, 2);
    const patchedBody = JSON.parse(String(fetchCalls[1].init.body)) as {
      event: string;
      ma: string;
      updated_at: string;
    };
    assert.equal(patchedBody.event, "update");
    assert.equal(patchedBody.ma, "A09");
    assert.equal(patchedBody.updated_at, patched.submission.updated_at);
    assertNoSecret(errors);
  });

  test("webhook reject still returns 200 with the submission", async () => {
    process.env.NEW_MA_WEBHOOK_URL = TEST_URL;
    process.env.NEW_MA_WEBHOOK_TOKEN = TEST_TOKEN;
    globalThis.fetch = (async () => {
      throw new Error(`ECONNREFUSED ${TEST_URL} ${TEST_TOKEN}`);
    }) as typeof fetch;

    const response = await POST(jsonForm("POST", "/api/submissions", { color: "Hồng" }));
    assert.equal(response.status, 200);
    const body = (await response.json()) as { submission: { ma: string; color: string } };
    assert.equal(body.submission.ma, "A01");
    assert.equal(body.submission.color, "Hồng");
    await flush();
    assert.equal(errors.length, 1);
    assert.deepEqual(errors[0][1], { event: "create", ma: "A01", status: "network" });
    assertNoSecret(errors);
    const disk = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
      submissions: { ma: string; color: string }[];
    };
    assert.equal(disk.submissions[0].ma, "A01");
    assert.equal(disk.submissions[0].color, "Hồng");
  });

  test("a webhook that sleeps does not hold the save response", async () => {
    process.env.NEW_MA_WEBHOOK_URL = TEST_URL;
    process.env.NEW_MA_WEBHOOK_TOKEN = TEST_TOKEN;
    let release = () => {};
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    globalThis.fetch = (async () => {
      await gate;
      return new Response("slow", { status: 500 });
    }) as typeof fetch;

    const started = Date.now();
    const pending = POST(jsonForm("POST", "/api/submissions"));
    try {
      const response = await Promise.race([
        pending,
        new Promise<Response>((_resolve, reject) => {
          setTimeout(() => reject(new Error("save blocked on webhook")), 1000);
        }),
      ]);
      const elapsed = Date.now() - started;
      assert.equal(response.status, 200);
      const body = (await response.json()) as { submission: { ma: string } };
      assert.equal(body.submission.ma, "A01");
      assert.ok(elapsed < 1000, `save took ${elapsed}ms`);
    } finally {
      release();
      await pending;
    }
  });

  test("HTTP 500 from the webhook still returns the submission", async () => {
    process.env.NEW_MA_WEBHOOK_URL = TEST_URL;
    process.env.NEW_MA_WEBHOOK_TOKEN = TEST_TOKEN;
    globalThis.fetch = (async () => new Response("nope", { status: 500 })) as typeof fetch;

    const response = await POST(jsonForm("POST", "/api/submissions"));
    assert.equal(response.status, 200);
    const body = (await response.json()) as { submission: { ma: string } };
    assert.equal(body.submission.ma, "A01");
    await flush();
    assert.deepEqual(errors[0][1], { event: "create", ma: "A01", status: 500 });
    assertNoSecret(errors);
  });
});

function sampleInput(overrides: Partial<NewMaWebhookInput> = {}): NewMaWebhookInput {
  return {
    event: "create",
    ma: "A17",
    updated_at: "2026-09-28T08:12:10.000Z",
    photo_count: 2,
    ...overrides,
  };
}

function jsonForm(method: "POST" | "PATCH", pathname: string, fields: Record<string, string> = {}): Request {
  const form = new FormData();
  form.set("kind", "A");
  form.set("size", "M");
  form.set("color", "Test");
  form.set("color_note", "webhook-test");
  form.set("link", "");
  form.set("pieces", "[]");
  form.set("keep_photos", "[]");
  for (const [key, value] of Object.entries(fields)) form.set(key, value);
  return new Request(`http://127.0.0.1${pathname}`, { method, body: form });
}

function flush(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 30));
}

function assertNoSecret(logs: unknown[][]): void {
  const dumped = JSON.stringify(logs);
  assert.equal(dumped.includes(TEST_TOKEN), false);
  assert.equal(dumped.includes(TEST_URL), false);
  assert.equal(dumped.includes("Bearer"), false);
  assert.equal(dumped.includes("Authorization"), false);
  assert.equal(dumped.includes("X-Automation-Key"), false);
}
