import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { intakeWriteErrorResponse, STORE_UNAVAILABLE_VI } from "../lib/store-unavailable";

function plainReq(): Request {
  return new Request("http://l/api/submissions");
}

async function withStore(raw: string | null, fn: () => Promise<void>) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-write-down-"));
  const saved = { ...process.env };
  for (const key of Object.keys(process.env)) if (/BLOB|KV_|VERCEL/.test(key)) delete process.env[key];
  process.env.SASSY_DATA_DIR = tmp;
  if (raw !== null) fs.writeFileSync(path.join(tmp, "submissions.json"), raw);
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    await fn();
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

function saveForm(kind = "A"): Request {
  const body = new FormData();
  body.set("kind", kind);
  body.set("size", "M");
  body.set("color", "Kem");
  return new Request("http://l/api/submissions", { method: "POST", body });
}

function rateRequest(rate: number): Request {
  return new Request("http://l/api/fx", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ usd_cny: rate }),
  });
}

async function assertStoreDown(res: Response, noindex = false) {
  assert.equal(res.status, 503);
  const body = await res.json();
  assert.equal(body.error, STORE_UNAVAILABLE_VI);
  assert.equal(body.storeUnavailable, true);
  const text = JSON.stringify(body);
  assert.equal(text.includes("https://"), false);
  assert.equal(text.includes("Kho mã đọc lỗi"), false);
  if (noindex) assert.match(res.headers.get("x-robots-tag") ?? "", /noindex/i);
}

test("a store failure on save or rate update is 503 and hides the raw error", async () => {
  const leaked = intakeWriteErrorResponse(new Error("Failed to fetch https://files.example/store"));
  assert.equal(leaked.status, 503);
  const leakedBody = await leaked.json();
  assert.equal(leakedBody.error, STORE_UNAVAILABLE_VI);
  assert.equal(JSON.stringify(leakedBody).includes("files.example"), false);

  const validation = intakeWriteErrorResponse(
    Object.assign(new Error("Loại đồ không đúng."), { status: 400 }),
  );
  assert.equal(validation.status, 400);
  assert.equal((await validation.json()).error, "Loại đồ không đúng.");

  await withStore("{not json", async () => {
    const list = await import("../app/api/submissions/route");
    const one = await import("../app/api/submissions/[ma]/route");
    const fx = await import("../app/api/fx/route");
    await assertStoreDown(await list.POST(saveForm()), true);
    await assertStoreDown(
      await one.PATCH(saveForm(), { params: Promise.resolve({ ma: "A01" }) }),
      true,
    );
    await assertStoreDown(await fx.POST(rateRequest(7)));
    const badRate = await fx.POST(rateRequest(0));
    assert.equal(badRate.status, 400);
    assert.equal((await badRate.json()).storeUnavailable, undefined);
  });
});

test("a bad kind or a missing mã stays a validation error when the store can be read", async () => {
  await withStore(null, async () => {
    const list = await import("../app/api/submissions/route");
    const one = await import("../app/api/submissions/[ma]/route");
    const badKind = await list.POST(saveForm("nope"));
    assert.equal(badKind.status, 400);
    const badBody = await badKind.json();
    assert.equal(badBody.error, "Loại đồ không đúng.");
    assert.equal(badBody.storeUnavailable, undefined);

    const missing = await one.PATCH(saveForm(), { params: Promise.resolve({ ma: "Z99" }) });
    assert.equal(missing.status, 404);
    assert.match((await missing.json()).error, /Không tìm thấy mã/);

    const created = await list.POST(saveForm());
    assert.equal(created.status, 200);
    const createdBody = await created.json();
    assert.equal(createdBody.submission.ma, "A01");
    assert.equal(createdBody.submission.color, "Kem");

    const notForm = new Request("http://l/api/submissions", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: "{}",
    });
    const badBodyResponse = await list.POST(notForm);
    assert.equal(badBodyResponse.status, 400);
    assert.equal((await badBodyResponse.json()).storeUnavailable, undefined);
    assert.equal(plainReq().url.endsWith("/api/submissions"), true);
  });
});
