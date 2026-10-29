import assert from "node:assert/strict";
import test from "node:test";
import { adminRequest } from "./admin-request";

// piece-253: optional empty-body 401; default stays JSON. Authorization unchanged.
const ctx = { params: Promise.resolve({ ma: "S06" }) };

async function hit(empty: string | undefined) {
  if (empty === undefined) delete process.env.SHOP_ADMIN_401_EMPTY;
  else process.env.SHOP_ADMIN_401_EMPTY = empty;
  const list = await import("../app/api/submissions/route");
  const one = await import("../app/api/submissions/[ma]/route");
  const exp = await import("../app/api/export/route");
  const ma = await import("../app/api/ma/[code]/route");
  const r = (m = "GET") => new Request("http://l/", { method: m, body: m === "GET" ? undefined : new FormData() });
  return [
    await list.GET(r()),
    await list.POST(r("POST")),
    await one.GET(r(), ctx),
    await one.PATCH(r("PATCH"), ctx),
    await exp.GET(r()),
    await ma.GET(r(), { params: Promise.resolve({ code: "S06" }) } as never),
  ];
}

test("default 401 keeps JSON body", async () => {
  const saved = { ...process.env };
  try {
    for (const res of await hit(undefined)) {
      assert.equal(res.status, 401);
      assert.deepEqual(await res.json(), { ok: false, error: "Unauthorized." });
      assert.match(res.headers.get("cache-control") ?? "", /no-store/);
    }
  } finally { process.env = saved; }
});

test("SHOP_ADMIN_401_EMPTY=1 gives truly empty 401 body", async () => {
  const saved = { ...process.env };
  try {
    for (const res of await hit("1")) {
      assert.equal(res.status, 401);
      assert.equal(await res.text(), "");
      assert.match(res.headers.get("cache-control") ?? "", /no-store/);
    }
  } finally { process.env = saved; }
});

test("helper modes + admin session still passes in both modes", async () => {
  const saved = { ...process.env };
  try {
    const { requireShopAdmin, shopAdmin401Mode } = await import("../lib/shop-admin-http");
    for (const v of ["0", "", "no"]) { process.env.SHOP_ADMIN_401_EMPTY = v; assert.equal(shopAdmin401Mode(), "json"); }
    for (const v of ["1", "TRUE", " yes "]) { process.env.SHOP_ADMIN_401_EMPTY = v; assert.equal(shopAdmin401Mode(), "empty"); }
    const unauth = new Request("http://l/");
    assert.equal(await (await requireShopAdmin(unauth, { mode: "empty" }))!.text(), "");
    assert.deepEqual(await (await requireShopAdmin(unauth, { mode: "json" }))!.json(), { ok: false, error: "Unauthorized." });
    for (const mode of ["json", "empty"] as const) {
      assert.equal(await requireShopAdmin(await adminRequest(), { mode }), null);
    }
  } finally { process.env = saved; }
});
