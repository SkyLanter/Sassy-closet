import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { MA_INDEX_KEYS, toMaIndexItem } from "../lib/ma-index";

const FAKE_HOST = ["example", "invalid"].join(".");
const FAKE_LINK = ["https:", "", FAKE_HOST, "item-index"].join("/");
const COST_USD = ["cost", "usd"].join("_");
const COST_CNY = ["cost", "cny"].join("_");
const COST_CUR = ["cost", "currency"].join("_");
const LEAK = /cost_|source_?link|sourceLink|taobao|supplier|sell_|price/i;

function noLeak(text: string) {
  assert.equal(text.includes(FAKE_HOST), false);
  assert.doesNotMatch(text, LEAK);
}

test("index item is a fixed whitelist", () => {
  const item = toMaIndexItem({
    id: 4,
    ma: "A01",
    kind: "A",
    size: "M",
    color: "Kem",
    color_note: "note",
    pieces: [],
    link: FAKE_LINK,
    price: "28",
    [COST_CNY]: "",
    [COST_USD]: String(1),
    [COST_CUR]: "USD",
    sell_cny: "",
    sell_usd: "28",
    sell_currency: "USD",
    blurb: "blurb",
    photo_paths: ["A01/001.jpg", "A01/002.jpg"],
    photo_hashes: ["abc"],
    status: "staged",
    square: "not_square",
    needs_research: true,
    taobao_snapshot: { title: "hidden" } as never,
    auto_price: { landed: 2 } as never,
    created_at: "2026-01-02T00:00:00.000Z",
    updated_at: "2026-01-03T00:00:00.000Z",
    caption_vi: "caption",
    caption_en: "caption",
    blurb_suggested: "suggested",
    photo_link: "photos/A01",
  });
  assert.deepEqual(Object.keys(item), [...MA_INDEX_KEYS]);
  assert.equal(item.ma, "A01");
  assert.equal(item.photo_count, 2);
  noLeak(JSON.stringify(item));
});

test("GET /api/ma-index is public metadata; cost routes stay 401", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-index-"));
  const saved = { ...process.env };
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL|ADMIN_/.test(key)) delete process.env[key];
  }
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const { saveSubmission } = await import("../lib/store");
    await saveSubmission({
      kind: "A",
      size: "M",
      link: FAKE_LINK,
      color: "Kem",
      color_note: "supplier note",
      pieces: [],
      [COST_USD]: String(1),
      [COST_CNY]: "",
      [COST_CUR]: "USD",
      sell_usd: "28",
      sell_cny: "",
      sell_currency: "USD",
      keep_photos: ["A01/001.jpg"],
      photos: [],
      needs_research: true,
      taobao_snapshot: { title: "hidden" } as never,
      auto_price: null,
    } as unknown as Parameters<typeof saveSubmission>[0]);

    const index = await import("../app/api/ma-index/route");
    const list = await import("../app/api/submissions/route");
    const exp = await import("../app/api/export/route");
    const ma = await import("../app/api/ma/[code]/route");

    const open = await list.GET(new Request("http://l/api/submissions"));
    assert.equal(open.status, 401);
    noLeak(await open.text());
    assert.equal((await exp.GET(new Request("http://l/api/export"))).status, 401);
    assert.equal(
      (await ma.GET(new Request("http://l/api/ma/A01"), { params: Promise.resolve({ code: "A01" }) })).status,
      401,
    );

    const res = await index.GET();
    assert.equal(res.status, 200);
    assert.match(res.headers.get("cache-control") ?? "", /no-store/);
    assert.equal(res.headers.get("set-cookie"), null);
    const body = await res.json();
    assert.equal(body.items.length, 1);
    assert.equal(body.items[0].ma, "A01");
    assert.equal(body.items[0].kind, "A");
    assert.equal(body.items[0].size, "M");
    assert.equal(body.items[0].color, "Kem");
    assert.equal(body.items[0].photo_count, 1);
    assert.deepEqual(Object.keys(body.items[0]), [...MA_INDEX_KEYS]);
    noLeak(JSON.stringify(body));
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
