import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import { captionStarter, editDeepLink, kindColorsLine } from "../lib/captions";
import { applyLocalFallback, createAsk, getAsk, replyAsk, webhookConfigured } from "../lib/ask-store";
import { formatMa, nextMa, parseHubMa } from "../lib/mint";

afterEach(() => {
  delete process.env.MINIBOSS_ASK_WEBHOOK_URL;
  delete process.env.MINIBOSS_ASK_WEBHOOK_KEY;
  delete process.env.ASK_REPLY_SECRET;
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

test("local fallback banner fields when webhook envs missing", async () => {
  assert.equal(webhookConfigured(), false);
  const pending = createAsk("size nào được?");
  const local = await applyLocalFallback(pending);
  assert.equal(local.status, "ready");
  assert.equal(local.source, "local");
  assert.equal(local.offline, true);
  assert.match(local.answer, /2XS/);
  const fetched = await getAsk(local.id);
  assert.equal(fetched?.offline, true);
});
