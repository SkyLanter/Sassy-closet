import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { saveFromForm } from "../lib/form-save";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { getSubmission, hashBytes, saveSubmission } from "../lib/store";
import { normalizeSourceLink } from "../lib/source-link";

/** Real-shape Taobao share blob: Chinese wrapper + short URL + 淘口令 tracking prose. */
const TAOBAO_SHARE_PASTE =
  "【淘宝】https://e.tb.cn/h.7KxYzAb  HU1234 「法式碎花连衣裙夏季新款」点击链接直接打开 或 复制这条信息￥abc123XYZ￥后打开👉淘宝👈";

const TAOBAO_SHARE_URL = "https://e.tb.cn/h.7KxYzAb";

describe("normalizeSourceLink", () => {
  test("extracts URL-only from a full Chinese Taobao share paste", () => {
    assert.match(TAOBAO_SHARE_PASTE, /【淘宝】/);
    assert.match(TAOBAO_SHARE_PASTE, /点击链接直接打开/);
    assert.equal(normalizeSourceLink(TAOBAO_SHARE_PASTE), TAOBAO_SHARE_URL);
  });

  test("accepts the full paste — does not reject wrapper text", () => {
    const extracted = normalizeSourceLink(TAOBAO_SHARE_PASTE);
    assert.ok(TAOBAO_SHARE_PASTE.includes(extracted));
    assert.notEqual(TAOBAO_SHARE_PASTE, extracted);
    assert.ok(!extracted.includes("淘宝"));
    assert.ok(!extracted.includes("￥"));
  });

  test("empty or whitespace paste stays empty — never invents a link", () => {
    assert.equal(normalizeSourceLink(""), "");
    assert.equal(normalizeSourceLink("   \n\t  "), "");
    assert.equal(normalizeSourceLink("点击链接直接打开 或 复制这条信息￥abc￥后打开👉淘宝👈"), "");
  });

  test("keeps an already-clean shop URL", () => {
    assert.equal(normalizeSourceLink("  https://e.tb.cn/h.abc  "), "https://e.tb.cn/h.abc");
    assert.equal(
      normalizeSourceLink("https://item.taobao.com/item.htm?id=123456"),
      "https://item.taobao.com/item.htm?id=123456",
    );
  });

  test("prefers e.tb.cn / tb.cn / taobao / tmall over a generic URL in the same paste", () => {
    assert.equal(
      normalizeSourceLink("size chart https://example.com/chart then shop https://e.tb.cn/h.pref01 extra"),
      "https://e.tb.cn/h.pref01",
    );
    assert.equal(
      normalizeSourceLink("8￥ CZ3457 3o7M2Ft9f0v￥休闲小零食 https://m.tb.cn/h.eeKwB12"),
      "https://m.tb.cn/h.eeKwB12",
    );
    assert.equal(
      normalizeSourceLink("see https://example.com/x and https://detail.tmall.com/item.htm?id=9"),
      "https://detail.tmall.com/item.htm?id=9",
    );
  });

  test("stops the URL before adjacent Chinese characters", () => {
    assert.equal(normalizeSourceLink("https://e.tb.cn/h.7KxYzAb点击链接"), TAOBAO_SHARE_URL);
  });
});

describe("source_link extract-on-save", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-link-"));
    for (const key of [
      "SASSY_DATA_DIR",
      "VERCEL",
      "BLOB_READ_WRITE_TOKEN",
      "BLOB_STORE_ID",
      "BLOB_ACCESS",
      "INTAKE_DATASET_SYNC_WEBHOOK_URL",
      "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
    ]) {
      prev[key] = process.env[key];
      delete process.env[key];
    }
    process.env.SASSY_DATA_DIR = tmp;
    resetStoreBackendForTests();
  });

  afterEach(() => {
    for (const [key, value] of Object.entries(prev)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("POST mint / form-save stores URL only from a full Chinese share paste", async () => {
    const form = mintForm({ link: TAOBAO_SHARE_PASTE, color: "Kem", size: "M" });
    const saved = await saveFromForm(form);
    assert.equal(saved.ma, "A01");
    assert.equal(saved.link, TAOBAO_SHARE_URL);
    assert.ok(!saved.link.includes("【"));
    assert.ok(!saved.link.includes("淘宝"));
    assert.equal(saved.color, "Kem");
    assert.equal(saved.size, "M");

    const disk = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
      submissions: { link: string }[];
    };
    assert.equal(disk.submissions[0].link, TAOBAO_SHARE_URL);
  });

  test("PATCH / Sửa extracts URL and does not wipe other fields or photos", async () => {
    const bytes = Buffer.from("keep-this-photo");
    const created = await saveSubmission({
      kind: "A",
      size: "M L",
      link: "",
      color: "Kem, Xanh",
      color_note: "pastel nhẹ",
      pieces: [],
      cost_usd: "12",
      cost_cny: "",
      cost_currency: "USD",
      sell_usd: "28",
      sell_cny: "",
      sell_currency: "USD",
      keep_photos: [],
      photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    });
    assert.equal(created.link, "");
    assert.deepEqual(created.photo_paths, ["A01/001.jpg"]);

    const form = mintForm({
      kind: created.kind,
      size: created.size,
      link: TAOBAO_SHARE_PASTE,
      color: created.color,
      color_note: created.color_note,
      cost_usd: created.cost_usd,
      cost_cny: created.cost_cny,
      cost_currency: created.cost_currency,
      sell_usd: created.sell_usd,
      sell_cny: created.sell_cny,
      sell_currency: created.sell_currency,
      keep_photos: JSON.stringify(created.photo_paths),
    });
    const patched = await saveFromForm(form, created.ma);
    assert.equal(patched.ma, created.ma);
    assert.equal(patched.link, TAOBAO_SHARE_URL);
    assert.equal(patched.color, "Kem, Xanh");
    assert.equal(patched.color_note, "pastel nhẹ");
    assert.equal(patched.size, "M L");
    assert.equal(patched.cost_usd, "12");
    assert.equal(patched.sell_usd, "28");
    assert.deepEqual(patched.photo_paths, ["A01/001.jpg"]);

    const fetched = await getSubmission(created.ma);
    assert.equal(fetched?.link, TAOBAO_SHARE_URL);
    assert.deepEqual(fetched?.photo_paths, ["A01/001.jpg"]);
  });

  test("empty / whitespace link stays empty on mint — no invented source link or extra mã", async () => {
    const saved = await saveFromForm(mintForm({ link: "  \n  ", color: "Đen" }));
    assert.equal(saved.ma, "A01");
    assert.equal(saved.link, "");
    const listed = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
      submissions: { ma: string }[];
    };
    assert.equal(listed.submissions.length, 1);
  });
});

function mintForm(overrides: Record<string, string> = {}): FormData {
  const form = new FormData();
  const defaults: Record<string, string> = {
    kind: "A",
    size: "",
    link: "",
    color: "",
    color_note: "",
    pieces: "[]",
    cost_usd: "",
    cost_cny: "",
    cost_currency: "USD",
    sell_usd: "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: "[]",
  };
  for (const [key, value] of Object.entries({ ...defaults, ...overrides })) {
    form.set(key, value);
  }
  return form;
}
