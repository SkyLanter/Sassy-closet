import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

test("submission writes are open without a session", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-253-"));
  const saved = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL|ADMIN_/.test(k)) delete process.env[k];
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const list = await import("../app/api/submissions/route");
    const one = await import("../app/api/submissions/[ma]/route");
    const form = new FormData();
    form.set("kind", "A");
    const posted = await list.POST(new Request("http://l/", { method: "POST", body: form }));
    assert.notEqual(posted.status, 401);
    const patched = await one.PATCH(
      new Request("http://l/", { method: "PATCH", body: form }),
      { params: Promise.resolve({ ma: "A01" }) },
    );
    assert.notEqual(patched.status, 401);
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("requireShopAdmin does not deny a request with no cookie", async () => {
  const { requireShopAdmin, shopAdmin401Mode } = await import("../lib/shop-admin-http");
  for (const v of ["0", "", "no"]) { process.env.SHOP_ADMIN_401_EMPTY = v; assert.equal(shopAdmin401Mode(), "json"); }
  for (const v of ["1", "TRUE", " yes "]) { process.env.SHOP_ADMIN_401_EMPTY = v; assert.equal(shopAdmin401Mode(), "empty"); }
  assert.equal(await requireShopAdmin(new Request("http://l/")), null);
});
