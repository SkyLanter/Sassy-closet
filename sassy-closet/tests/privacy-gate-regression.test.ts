import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

// Direct-link reads and writes are public and noindex. No session cookie.
const NOINDEX = /noindex,\s*nofollow,\s*nosnippet/i;

async function writeRoutes() {
  const list = await import("../app/api/submissions/route");
  const one = await import("../app/api/submissions/[ma]/route");
  const maCtx = { params: Promise.resolve({ ma: "S06" }) };
  const fd = () => { const f = new FormData(); f.set("ma", "S06"); f.set("sell_usd", "25"); return f; };
  const json = () => JSON.stringify({ ma: "S06", sell_usd: 25 });
  const req = (method: string, body?: BodyInit, ct?: string) =>
    new Request("http://l/", { method, body, headers: ct ? { "content-type": ct } : undefined });
  return [
    ["POST /api/submissions form", () => list.POST(req("POST", fd()))],
    ["POST /api/submissions json", () => list.POST(req("POST", json(), "application/json"))],
    ["PATCH /api/submissions/[ma] form", () => one.PATCH(req("PATCH", fd()), maCtx)],
    ["PATCH /api/submissions/[ma] json", () => one.PATCH(req("PATCH", json(), "application/json"), maCtx)],
  ] as Array<[string, () => Promise<Response>]>;
}

function assertNoindex(res: Response, name: string) {
  assert.match(res.headers.get("x-robots-tag") ?? "", NOINDEX, name);
  assert.match(res.headers.get("cache-control") ?? "", /no-store/, name);
  assert.equal(res.headers.get("set-cookie"), null, name);
}

test("unauthenticated intake writes are not 401 and set no cookie", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-direct-write-"));
  const saved = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL|ADMIN_/.test(k)) delete process.env[k];
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    for (const [name, call] of await writeRoutes()) {
      const res = await call();
      assert.notEqual(res.status, 401, name);
      assertNoindex(res, name);
    }
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
