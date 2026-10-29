import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { ADMIN_SESSION_COOKIE } from "../lib/admin-auth";
import { adminRequest } from "./admin-request";

// Placeholders only — no real costs / supplier links.
const FAKE_HOST = ["example", "invalid"].join(".");
const FAKE_LINK = ["https:", "", FAKE_HOST, "item-240b"].join("/");
const COST_USD = ["cost", "usd"].join("_");
const COST_CNY = ["cost", "cny"].join("_");
const COST_CUR = ["cost", "currency"].join("_");

function noLeak(text: string) {
  assert.ok(!text.includes(FAKE_HOST), "no source link in 401");
  assert.ok(!text.includes("cost_"), "no cost fields in 401");
}

test("GET /api/submissions, /api/submissions/[ma], /api/ma/[code]: 401 unauth, 200 with session", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-240b-"));
  const saved = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL|ADMIN_/.test(k)) delete process.env[k];
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const { saveSubmission } = await import("../lib/store");
    await saveSubmission({
      kind: "A", size: "M", link: FAKE_LINK, color: "Kem", color_note: "", pieces: [],
      [COST_USD]: String(1), [COST_CNY]: "", [COST_CUR]: "USD", sell_usd: "28", sell_cny: "", sell_currency: "USD",
      keep_photos: [], photos: [], needs_research: false, taobao_snapshot: null, auto_price: null,
    } as unknown as Parameters<typeof saveSubmission>[0]);
    const list = await import("../app/api/submissions/route");
    const one = await import("../app/api/submissions/[ma]/route");
    const ma = await import("../app/api/ma/[code]/route");
    const calls = [
      (r: Request) => list.GET(r),
      (r: Request) => one.GET(r, { params: Promise.resolve({ ma: "A01" }) }),
      (r: Request) => ma.GET(r, { params: Promise.resolve({ code: "A01" }) }),
    ];

    // auth not configured, no cookie, forged cookie -> 401, no leak
    for (const call of calls) {
      const a = await call(new Request("http://l/"));
      assert.equal(a.status, 401);
      noLeak(await a.text());
    }
    const authed = await adminRequest(); // configures auth for the rest
    for (const call of calls) {
      const b = await call(new Request("http://l/"));
      assert.equal(b.status, 401);
      noLeak(await b.text());
      const c = await call(new Request("http://l/", { headers: { cookie: `${ADMIN_SESSION_COOKIE}=forged` } }));
      assert.equal(c.status, 401);
      noLeak(await c.text());
    }

    // with session -> same shape as before
    const l = await list.GET(authed);
    assert.equal(l.status, 200);
    const lb = await l.json();
    assert.equal(lb.submissions[0].ma, "A01");
    assert.ok("storage" in lb && "catalog" in lb);
    const o = await one.GET(await adminRequest(), { params: Promise.resolve({ ma: "a1" }) });
    assert.equal(o.status, 200);
    const ob = await o.json();
    assert.equal(ob.ma, "A01");
    assert.ok(ob.submission && "caption_vi" in ob);
    const m = await ma.GET(await adminRequest(), { params: Promise.resolve({ code: "A01" }) });
    assert.equal(m.status, 200);
    assert.equal((await m.json()).code, "A01");
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
