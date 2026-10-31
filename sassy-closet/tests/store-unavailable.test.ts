import assert from "node:assert/strict";
import { test } from "node:test";
import { storeErrorReason, storeUnavailableResponse } from "../lib/store-unavailable";

test("blocked Blob store read maps to 503 with no secrets", async () => {
  const err = new Error("Vercel Blob: This store is blocked. token=vercel_blob_rw_SECRET");
  assert.equal(storeErrorReason(err), "store-blocked");
  const res = storeUnavailableResponse(err);
  assert.equal(res.status, 503);
  assert.notEqual(res.status, 401);
  assert.match(res.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
  assert.match(res.headers.get("cache-control") ?? "", /no-store/);
  const body = await res.json();
  assert.equal(body.storeUnavailable, true);
  const text = JSON.stringify(body);
  assert.equal(text.includes("SECRET"), false);
  assert.equal(text.toLowerCase().includes("vercel_blob"), false);
  assert.equal(text.toLowerCase().includes("token"), false);
});

test("other failures classify without leaking", () => {
  assert.equal(storeErrorReason(new Error("403 Forbidden")), "forbidden");
  assert.equal(storeErrorReason(new Error("fetch failed")), "network");
  assert.equal(storeErrorReason("weird"), "read-failed");
});
