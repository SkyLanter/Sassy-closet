import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

test("POST/PATCH submissions save without a session or cookie", async () => {
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
    const form = () => { const f = new FormData(); f.set("kind", "A"); f.set("size", "M"); f.set("sell_usd", ""); return f; };
    const created = await list.POST(new Request("http://l/", { method: "POST", body: form() }));
    assert.equal(created.status, 200);
    assert.equal(created.headers.get("set-cookie"), null);
    assert.match(created.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
    const body = (await created.json()) as { submission: { ma: string; sell_usd: string } };
    assert.equal(body.submission.ma, "A01");
    assert.equal(body.submission.sell_usd, "");
    const patched = await one.PATCH(
      new Request("http://l/", { method: "PATCH", body: form() }),
      { params: Promise.resolve({ ma: "A01" }) },
    );
    assert.equal(patched.status, 200);
    assert.equal((await listSubmissions()).length, 1);
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
