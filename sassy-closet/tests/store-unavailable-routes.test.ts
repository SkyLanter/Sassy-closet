import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { STORE_UNAVAILABLE_VI } from "../lib/store-unavailable";

function plainReq(): Request {
  return new Request("http://l/api/export");
}

// Simulate "store can't be read" with a corrupt local store file: same throw path
// as a blocked Blob store (readStore throws), no network, no Blob.
async function withStore(raw: string | null, fn: () => Promise<void>) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-233b-"));
  const saved = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL/.test(k)) delete process.env[k];
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

async function is503(res: Response, directLink = false) {
  assert.equal(res.status, 503);
  const body = await res.json();
  assert.equal(body.error, STORE_UNAVAILABLE_VI);
  assert.equal(body.storeUnavailable, true);
  if (directLink) assert.match(res.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
}

function photoForm() {
  const form = new FormData();
  form.set("photo", new File([Buffer.from("x")], "a.jpg", { type: "image/jpeg" }));
  return new Request("http://localhost/api/find-ma", { method: "POST", body: form });
}

test("store read failure -> 503 + Vietnamese message on read routes", async () => {
  await withStore("{not json", async () => {
    const one = await import("../app/api/submissions/[ma]/route");
    await is503(await one.GET(plainReq(), { params: Promise.resolve({ ma: "S06" }) }), true);
    const list = await import("../app/api/submissions/route");
    await is503(await list.GET(), true);
    const fx = await import("../app/api/fx/route");
    await is503(await fx.GET());
    const exp = await import("../app/api/export/route");
    await is503(await exp.GET(), true);
    const find = await import("../app/api/find-ma/route");
    await is503(await find.POST(photoForm()));
    const ma = await import("../app/api/ma/[code]/route");
    await is503(await ma.GET(plainReq(), { params: Promise.resolve({ code: "A01" }) }), true);
  });
});

test("success paths unchanged on an empty healthy store", async () => {
  await withStore(null, async () => {
    const one = await import("../app/api/submissions/[ma]/route");
    const missing = await one.GET(plainReq(), { params: Promise.resolve({ ma: "Z99" }) });
    assert.equal(missing.status, 404);
    assert.match(missing.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
    const exp = await import("../app/api/export/route");
    const r = await exp.GET();
    assert.equal(r.status, 200);
    assert.match(r.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
    assert.match(r.headers.get("content-type") ?? "", /text\/csv/);
    const find = await import("../app/api/find-ma/route");
    const f = await find.POST(photoForm());
    assert.equal(f.status, 200);
    assert.deepEqual((await f.json()).matches, []);
    const ph = await import("../app/api/photos/[...path]/route");
    assert.equal((await ph.GET(new Request("http://l/"), { params: Promise.resolve({ path: ["A01", "001.jpg"] }) })).status, 404);
    assert.equal((await ph.GET(new Request("http://l/"), { params: Promise.resolve({ path: ["..", "x.jpg"] }) })).status, 404);
  });
});

test("photo read failure (not a bad path) -> 503", async () => {
  await withStore(null, async () => {
    // a directory where the photo file should be -> read throws (EISDIR)
    fs.mkdirSync(path.join(process.env.SASSY_DATA_DIR!, "photos", "A01", "001.jpg"), { recursive: true });
    const ph = await import("../app/api/photos/[...path]/route");
    const res = await ph.GET(new Request("http://l/"), { params: Promise.resolve({ path: ["A01", "001.jpg"] }) });
    await is503(res);
  });
});
