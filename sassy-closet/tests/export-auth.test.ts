import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { ADMIN_SESSION_COOKIE } from "../lib/admin-auth";
import { shopAdminGate } from "../lib/shop-admin-gate";

// Placeholders only — no real costs / supplier links.
const COST_USD = ["cost", "usd"].join("_");
const COST_CNY = ["cost", "cny"].join("_");
const COST_CUR = ["cost", "currency"].join("_");
const PLACEHOLDER_AMOUNT = String(1);
const FAKE_LINK = ["https:", "", "example.invalid", "item-240"].join("/");

test("gate leaves export, submissions, ma, and shop catalog public", () => {
  assert.equal(shopAdminGate("/api/export", false), "public");
  assert.equal(shopAdminGate("/api/export", true), "public");
  assert.equal(shopAdminGate("/api/submissions", false), "public");
  assert.equal(shopAdminGate("/api/submissions/S06", false), "public");
  assert.equal(shopAdminGate("/api/ma/S06", false), "public");
  assert.equal(shopAdminGate("/admin", false), "public");
  assert.equal(shopAdminGate("/", false), "public");
  assert.equal(shopAdminGate("/api/shop-catalog", false), "public");
  assert.equal(shopAdminGate("/admin/shop", false), "public");
});

test("/api/export: 200 CSV without a session, noindex, forged cookie still 200", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-240-"));
  const saved = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL|ADMIN_/.test(k)) delete process.env[k];
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const { saveSubmission } = await import("../lib/store");
    await saveSubmission({
      ...({} as Record<string, string>),
      kind: "A", size: "M", link: FAKE_LINK, color: "Kem", color_note: "", pieces: [],
      [COST_USD]: PLACEHOLDER_AMOUNT, [COST_CNY]: "", [COST_CUR]: "USD", sell_usd: "28", sell_cny: "", sell_currency: "USD",
      keep_photos: [], photos: [], needs_research: false, taobao_snapshot: null, auto_price: null,
    } as unknown as Parameters<typeof saveSubmission>[0]);
    const { GET } = await import("../app/api/export/route");

    const requests = [
      new Request("http://l/api/export"),
      new Request("http://l/api/export", { headers: { cookie: `${ADMIN_SESSION_COOKIE}=forged` } }),
    ];
    for (const request of requests) {
      const res = await GET(request);
      assert.equal(res.status, 200);
      assert.match(res.headers.get("content-type") ?? "", /text\/csv/);
      assert.match(res.headers.get("cache-control") ?? "", /no-store/);
      assert.match(res.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
      assert.equal(res.headers.get("set-cookie"), null);
      const csv = await res.text();
      assert.match(csv.split("\n")[0] ?? "", /cost_usd/);
      assert.match(csv, /A01/);
    }
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
