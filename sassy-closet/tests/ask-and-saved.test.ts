import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";
import { localAskAnswer } from "../lib/ask-fallback";
import { captionStarter, editDeepLink, kindColorsLine } from "../lib/captions";
import { applyLocalFallback, createAsk, getAsk, replyAsk, webhookConfigured } from "../lib/ask-store";
import { formatMa, nextMa, parseHubMa } from "../lib/mint";
import { saveSubmission } from "../lib/store";

type StoreCache = typeof globalThis & { __sassyStore?: unknown };

function resetIsolatedStore(): void {
  process.env.SASSY_DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-ask-"));
  delete (globalThis as StoreCache).__sassyStore;
}

afterEach(() => {
  delete process.env.MINIBOSS_ASK_WEBHOOK_URL;
  delete process.env.MINIBOSS_ASK_WEBHOOK_KEY;
  delete process.env.ASK_REPLY_SECRET;
  delete process.env.SASSY_DATA_DIR;
  delete (globalThis as StoreCache).__sassyStore;
});

test("caption starter is mã on line 1", () => {
  assert.equal(captionStarter("a01"), "A01");
  assert.equal(kindColorsLine({ kind: "A", color: "Kem, Xanh" }), "Áo · Kem, Xanh");
  assert.equal(
    editDeepLink("https://sassy-closet.vercel.app/foo", "P05"),
    "https://sassy-closet.vercel.app/?ma=P05",
  );
});

test("mint next mã without inventing extras", () => {
  assert.deepEqual(parseHubMa("A01"), { kind: "A", n: 1 });
  assert.equal(nextMa("P", ["P01", "P02", "P05"]), "P06");
  assert.equal(formatMa("A", 100), "A100");
});

test("ask stays waiting until reply when webhook envs exist", () => {
  process.env.MINIBOSS_ASK_WEBHOOK_URL = "https://example.invalid/hook";
  process.env.MINIBOSS_ASK_WEBHOOK_KEY = "hook-key";
  assert.equal(webhookConfigured(), true);
  const pending = createAsk("còn A01 không?");
  assert.equal(pending.status, "waiting");
  const replied = replyAsk(pending.id, "Còn trên site. Copy thôi — không Post.");
  assert.equal(replied.status, "ready");
  assert.equal(replied.source, "relay");
  assert.equal(replied.offline, false);
});

test("local fallback banner fields when webhook envs missing", () => {
  assert.equal(webhookConfigured(), false);
  const pending = createAsk("size nào được?");
  const local = applyLocalFallback(pending);
  assert.equal(local.status, "ready");
  assert.equal(local.source, "local");
  assert.equal(local.offline, true);
  assert.match(local.answer, /2XS/);
  const fetched = getAsk(local.id);
  assert.equal(fetched?.offline, true);
});

test("size plus mã reports the saved size, not the generic size list", () => {
  resetIsolatedStore();
  const saved = saveSubmission({
    kind: "A",
    size: "M L",
    link: "",
    color: "Kem",
    color_note: "",
    pieces: [],
    cost_usd: "",
    cost_cny: "",
    cost_currency: "USD",
    sell_usd: "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: [],
    photos: [],
    newMa: "A01",
  });
  assert.equal(saved.ma, "A01");

  const withMa = localAskAnswer("size A01");
  assert.match(withMa.reply, /A01 size đã lưu: M L/);
  assert.doesNotMatch(withMa.reply, /Gõ mã nếu muốn xem size đã lưu/);
  assert.deepEqual(withMa.copies, [{ id: "size", label: "Copy size", text: "M L" }]);

  const flipped = localAskAnswer("A01 size bao nhiêu");
  assert.match(flipped.reply, /A01 size đã lưu: M L/);

  const generic = localAskAnswer("size nào được?");
  assert.match(generic.reply, /Gõ mã nếu muốn xem size đã lưu/);
  assert.doesNotMatch(generic.reply, /size đã lưu:/);

  const missing = localAskAnswer("size A99");
  assert.match(missing.reply, /Không thấy A99/);
  assert.doesNotMatch(missing.reply, /size đã lưu:/);
});
