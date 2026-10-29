import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { NextRequest } from "next/server";
import { ADMIN_SESSION_COOKIE } from "../lib/admin-auth";
import { middleware } from "../middleware";
import { adminRequest } from "./admin-request";

const SECRET = ["pipeline", "test", "secret", "abcd"].join("-");
const FAKE_LINK = ["https:", "", "example.invalid", "item-pipe"].join("/");
const COST_USD = ["cost", "usd"].join("_");
const COST_CNY = ["cost", "cny"].join("_");
const COST_CUR = ["cost", "currency"].join("_");

function noLeak(text: string) {
  assert.equal(text.includes(SECRET), false);
  assert.equal(text.includes("example.invalid"), false);
  assert.equal(text.includes("cost_"), false);
}

function withBearer(secret: string, method = "GET", body?: BodyInit): Request {
  return new Request("http://l/", {
    method,
    body,
    headers: { authorization: `Bearer ${secret}` },
  });
}

test("bearer shape: usable secret, Bearer scheme, GET only", async () => {
  const saved = { ...process.env };
  try {
    delete process.env.INTAKE_PIPELINE_SECRET;
    delete process.env.ADMIN_PASSWORD;
    delete process.env.ADMIN_SESSION_SECRET;
    const { pipelineBearerOk, pipelineSecretUsable, readPipelineBearer } = await import("../lib/pipeline-auth");
    const { requireIntakeRead, requireShopAdmin } = await import("../lib/shop-admin-http");

    assert.equal(pipelineSecretUsable("a".repeat(23)), false);
    assert.equal(pipelineSecretUsable("a".repeat(24)), true);
    assert.equal(pipelineSecretUsable("a".repeat(256)), true);
    assert.equal(pipelineSecretUsable("a".repeat(257)), false);
    assert.equal(pipelineSecretUsable(`${SECRET} tail`), false);
    assert.equal(readPipelineBearer(new Request("http://l/", { headers: { authorization: SECRET } })), "");
    assert.equal(readPipelineBearer(new Request(`http://l/?token=${SECRET}`)), "");

    assert.equal(await pipelineBearerOk(withBearer(SECRET)), false);
    process.env.INTAKE_PIPELINE_SECRET = `  ${SECRET}  `;
    assert.equal(await pipelineBearerOk(withBearer(SECRET)), true);
    assert.equal(await pipelineBearerOk(withBearer(`${SECRET}x`)), false);
    assert.equal(await pipelineBearerOk(new Request("http://l/", { headers: { "x-intake-pipeline-key": SECRET } })), false);
    const sessionOnly = await requireShopAdmin(withBearer(SECRET));
    assert.equal(sessionOnly?.status, 401);
    assert.equal(await requireIntakeRead(withBearer(SECRET)), null);
    const posted = await requireIntakeRead(withBearer(SECRET, "POST", new FormData()));
    assert.equal(posted?.status, 401);
    process.env.INTAKE_PIPELINE_SECRET = "a".repeat(23);
    const short = await requireIntakeRead(withBearer("a".repeat(23)));
    assert.equal(short?.status, 401);
  } finally {
    process.env = saved;
  }
});

test("machine GET reads the mã list; public and writes stay 401", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-pipe-"));
  const saved = { ...process.env };
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL|ADMIN_|INTAKE_PIPELINE/.test(key)) delete process.env[key];
  }
  process.env.SASSY_DATA_DIR = tmp;
  delete process.env.SHOP_ADMIN_401_EMPTY;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const { saveSubmission, listSubmissions } = await import("../lib/store");
    await saveSubmission({
      kind: "A", size: "M", link: FAKE_LINK, color: "Kem", color_note: "", pieces: [],
      [COST_USD]: String(1), [COST_CNY]: "", [COST_CUR]: "USD", sell_usd: "28", sell_cny: "", sell_currency: "USD",
      keep_photos: [], photos: [], needs_research: false, taobao_snapshot: null, auto_price: null,
    } as unknown as Parameters<typeof saveSubmission>[0]);

    const list = await import("../app/api/submissions/route");
    const one = await import("../app/api/submissions/[ma]/route");
    const ma = await import("../app/api/ma/[code]/route");
    const exp = await import("../app/api/export/route");
    const shop = await import("../app/api/shop-catalog/route");
    const maCtx = { params: Promise.resolve({ ma: "A01" }) };
    const codeCtx = { params: Promise.resolve({ code: "A01" }) };
    const missingCtx = { params: Promise.resolve({ ma: "Z99" }) };

    process.env.INTAKE_PIPELINE_SECRET = SECRET;
    const open = await list.GET(new Request("http://l/api/submissions"));
    assert.equal(open.status, 401);
    noLeak(await open.text());

    const query = await list.GET(new Request(`http://l/api/submissions?access_token=${SECRET}`));
    assert.equal(query.status, 401);
    noLeak(await query.text());

    const wrong = await list.GET(withBearer(`${SECRET}x`));
    assert.equal(wrong.status, 401);
    noLeak(await wrong.text());
    assert.match(wrong.headers.get("cache-control") ?? "", /no-store/);

    const reads = [
      await list.GET(withBearer(SECRET)),
      await one.GET(withBearer(SECRET), maCtx),
      await ma.GET(withBearer(SECRET), codeCtx),
      await exp.GET(new Request("http://l/api/export", { headers: { authorization: `Bearer ${SECRET}` } })),
    ];
    assert.deepEqual(reads.map((res) => res.status), [200, 200, 200, 200]);
    for (const res of reads) {
      assert.match(res.headers.get("cache-control") ?? "", /private/);
      assert.match(res.headers.get("cache-control") ?? "", /no-store/);
      assert.equal(res.headers.get("set-cookie"), null);
    }
    const listed = await reads[0].json();
    assert.equal(listed.submissions[0].ma, "A01");
    assert.equal(JSON.stringify(listed).includes(SECRET), false);
    const single = await reads[1].json();
    assert.equal(single.ma, "A01");
    const card = await reads[2].json();
    assert.equal(card.code, "A01");
    const csv = await reads[3].text();
    assert.match(csv, /A01/);
    assert.match(reads[3].headers.get("content-type") ?? "", /text\/csv/);

    const lower = await list.GET(new Request("http://l/", { headers: { authorization: `bearer ${SECRET}` } }));
    assert.equal(lower.status, 200);
    const spaced = await list.GET(new Request("http://l/", { headers: { authorization: `Bearer  ${SECRET}` } }));
    assert.equal(spaced.status, 200);

    const missing = await one.GET(withBearer(SECRET), missingCtx);
    assert.equal(missing.status, 404);
    assert.match(missing.headers.get("cache-control") ?? "", /no-store/);

    const before = (await listSubmissions()).length;
    const form = () => {
      const body = new FormData();
      body.set("kind", "A");
      body.set("size", "M");
      return body;
    };
    const posted = await list.POST(withBearer(SECRET, "POST", form()));
    assert.equal(posted.status, 401);
    noLeak(await posted.text());
    const patched = await one.PATCH(withBearer(SECRET, "PATCH", form()), maCtx);
    assert.equal(patched.status, 401);
    noLeak(await patched.text());
    assert.equal((await listSubmissions()).length, before);

    const shopDenied = await shop.GET(withBearer(SECRET));
    assert.equal(shopDenied.status, 401);
    noLeak(await shopDenied.text());

    process.env.SHOP_ADMIN_401_EMPTY = "1";
    const empty = await list.GET(new Request("http://l/"));
    assert.equal(empty.status, 401);
    assert.equal(await empty.text(), "");
    delete process.env.SHOP_ADMIN_401_EMPTY;

    process.env.INTAKE_PIPELINE_SECRET = "b".repeat(256);
    assert.equal((await list.GET(withBearer("b".repeat(256)))).status, 200);
    process.env.INTAKE_PIPELINE_SECRET = "c".repeat(257);
    const oversized = await list.GET(withBearer("c".repeat(257)));
    assert.equal(oversized.status, 401);
    assert.equal((await oversized.text()).includes("c".repeat(24)), false);

    const authed = await adminRequest();
    delete process.env.INTAKE_PIPELINE_SECRET;
    const session = await list.GET(authed);
    assert.equal(session.status, 200);
    const stillLocked = await list.GET(new Request("http://l/", { headers: { cookie: `${ADMIN_SESSION_COOKIE}=forged` } }));
    assert.equal(stillLocked.status, 401);
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("middleware allows export GET with the bearer and keeps shop tools locked", async () => {
  const saved = { ...process.env };
  try {
    delete process.env.INTAKE_PIPELINE_SECRET;
    delete process.env.ADMIN_PASSWORD;
    delete process.env.ADMIN_SESSION_SECRET;
    const locked = await middleware(new NextRequest("http://127.0.0.1/api/export"));
    assert.equal(locked.status, 401);

    process.env.INTAKE_PIPELINE_SECRET = SECRET;
    const shop = await middleware(
      new NextRequest("http://127.0.0.1/api/shop-catalog", { headers: { authorization: `Bearer ${SECRET}` } }),
    );
    assert.equal(shop.status, 401);
    const page = await middleware(
      new NextRequest("http://127.0.0.1/admin/shop", { headers: { authorization: `Bearer ${SECRET}` } }),
    );
    assert.equal(page.status, 307);
    const csv = await middleware(
      new NextRequest("http://127.0.0.1/api/export", { headers: { authorization: `Bearer ${SECRET}` } }),
    );
    assert.equal(csv.status, 200);
    const post = await middleware(
      new NextRequest("http://127.0.0.1/api/export", {
        method: "POST",
        headers: { authorization: `Bearer ${SECRET}` },
      }),
    );
    assert.equal(post.status, 401);
    const wrong = await middleware(
      new NextRequest("http://127.0.0.1/api/export", { headers: { authorization: `Bearer ${SECRET}x` } }),
    );
    assert.equal(wrong.status, 401);
    assert.equal((await wrong.text()).includes(SECRET), false);
    process.env.INTAKE_PIPELINE_SECRET = "a".repeat(23);
    const short = await middleware(
      new NextRequest("http://127.0.0.1/api/export", { headers: { authorization: "Bearer " + "a".repeat(23) } }),
    );
    assert.equal(short.status, 401);
  } finally {
    process.env = saved;
  }
});
