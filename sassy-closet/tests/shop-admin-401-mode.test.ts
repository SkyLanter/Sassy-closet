import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

test("intake writes are not a 401 without a session", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-253-"));
  const saved = { ...process.env };
  for (const key of Object.keys(process.env)) if (/BLOB|KV_|VERCEL|ADMIN_/.test(key)) delete process.env[key];
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const list = await import("../app/api/submissions/route");
    const one = await import("../app/api/submissions/[ma]/route");
    const posted = await list.POST(new Request("http://l/", { method: "POST", body: new FormData() }));
    const patched = await one.PATCH(
      new Request("http://l/", { method: "PATCH", body: new FormData() }),
      { params: Promise.resolve({ ma: "A01" }) },
    );
    assert.notEqual(posted.status, 401);
    assert.notEqual(patched.status, 401);
    assert.match(posted.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
    assert.match(patched.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("requireShopAdmin does not deny a request with no cookie", async () => {
  const { requireShopAdmin } = await import("../lib/shop-admin-http");
  assert.equal(await requireShopAdmin(new Request("http://l/")), null);
});
