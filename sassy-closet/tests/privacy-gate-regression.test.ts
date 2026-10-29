import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

// Direct-link reads and writes are public and noindex. There is no session wall.
const NOINDEX = /noindex,\s*nofollow,\s*nosnippet/i;

function assertNoindex(res: Response, name: string) {
  assert.match(res.headers.get("x-robots-tag") ?? "", NOINDEX, name);
  assert.match(res.headers.get("cache-control") ?? "", /no-store/, name);
  assert.equal(res.headers.get("set-cookie"), null, name);
}

test("intake writes are open and noindex without a session", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-open-write-"));
  const saved = { ...process.env };
  for (const key of Object.keys(process.env)) if (/BLOB|KV_|VERCEL|ADMIN_/.test(key)) delete process.env[key];
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const list = await import("../app/api/submissions/route");
    const one = await import("../app/api/submissions/[ma]/route");
    const form = new FormData();
    form.set("kind", "A");
    form.set("size", "S");
    const posted = await list.POST(new Request("http://l/", { method: "POST", body: form }));
    assert.notEqual(posted.status, 401);
    assertNoindex(posted, "POST");
    const patched = await one.PATCH(
      new Request("http://l/", { method: "PATCH", body: new FormData() }),
      { params: Promise.resolve({ ma: "A01" }) },
    );
    assert.notEqual(patched.status, 401);
    assertNoindex(patched, "PATCH");
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("unauthenticated intake reads are 200 or 404 with noindex and no cookie", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-direct-"));
  const saved = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL|ADMIN_/.test(k)) delete process.env[k];
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const list = await import("../app/api/submissions/route");
    const one = await import("../app/api/submissions/[ma]/route");
    const exp = await import("../app/api/export/route");
    const ma = await import("../app/api/ma/[code]/route");
    const req = () => new Request("http://l/");
    const reads: Array<[string, number, () => Promise<Response>]> = [
      ["GET /api/submissions", 200, () => list.GET()],
      ["GET /api/submissions/S06", 404, () => one.GET(req(), { params: Promise.resolve({ ma: "S06" }) })],
      ["GET /api/export", 200, () => exp.GET()],
      ["GET /api/ma/S06", 404, () => ma.GET(req(), { params: Promise.resolve({ code: "S06" }) })],
    ];
    for (const [name, status, call] of reads) {
      const res = await call();
      assert.equal(res.status, status, name);
      assertNoindex(res, name);
      if (name === "GET /api/export") assert.match(res.headers.get("content-type") ?? "", /text\/csv/);
    }
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
