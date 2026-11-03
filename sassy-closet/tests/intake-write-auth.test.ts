import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

test("POST/PATCH submissions save without a session cookie", async () => {
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
    const form = () => {
      const body = new FormData();
      body.set("kind", "A");
      body.set("size", "M");
      return body;
    };
    const created = await list.POST(new Request("http://l/", { method: "POST", body: form() }));
    assert.notEqual(created.status, 401);
    assert.equal(created.headers.get("set-cookie"), null);
    assert.match(created.headers.get("x-robots-tag") ?? "", /noindex/);
    const rows = await listSubmissions();
    assert.equal(rows.length, 1);
    const patched = await one.PATCH(
      new Request("http://l/", { method: "PATCH", body: form() }),
      { params: Promise.resolve({ ma: rows[0]?.ma ?? "A01" }) },
    );
    assert.notEqual(patched.status, 401);
    assert.equal((await listSubmissions()).length, 1);
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
