import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { ADMIN_SESSION_COOKIE } from "../lib/admin-auth";
import { adminRequest } from "./admin-request";

// piece-245: POST /api/submissions and PATCH /api/submissions/[ma] need an admin session.
test("POST/PATCH submissions: 401 unauth/forged, store untouched; session passes the gate", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-245-"));
  const saved = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL|ADMIN_/.test(k)) delete process.env[k];
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const list = await import("../app/api/submissions/route");
    const one = await import("../app/api/submissions/[ma]/route");
    const { listSubmissions } = await import("../lib/store");
    const form = () => { const f = new FormData(); f.set("kind", "A"); f.set("size", "M"); return f; };
    const post = (h?: Record<string, string>) => new Request("http://l/", { method: "POST", body: form(), headers: h });
    const ctx = { params: Promise.resolve({ ma: "A01" }) };
    const calls = [
      (h?: Record<string, string>) => list.POST(post(h)),
      (h?: Record<string, string>) => one.PATCH(new Request("http://l/", { method: "PATCH", body: form(), headers: h }), ctx),
    ];
    for (const call of calls) {
      assert.equal((await call()).status, 401);
    }
    await adminRequest(); // configure auth
    for (const call of calls) {
      const a = await call();
      assert.equal(a.status, 401);
      const t = await a.text();
      assert.ok(!t.includes("cost_") && !t.includes("submission"));
      assert.equal((await call({ cookie: `${ADMIN_SESSION_COOKIE}=forged` })).status, 401);
    }
    assert.equal((await listSubmissions()).length, 0, "nothing saved by unauth writes");
    const authed = await adminRequest();
    const ok = await list.POST(new Request("http://l/", { method: "POST", body: form(), headers: { cookie: authed.headers.get("cookie")! } }));
    assert.notEqual(ok.status, 401, "session passes the gate");
    const p = await one.PATCH(new Request("http://l/", { method: "PATCH", body: form(), headers: { cookie: authed.headers.get("cookie")! } }), ctx);
    assert.notEqual(p.status, 401);
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
