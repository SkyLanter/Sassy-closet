import assert from "node:assert/strict";
import { test } from "node:test";
import { storeErrorReason, storeUnavailableResponse } from "../lib/store-unavailable";

test("blocked Blob store read maps to 503 with no secrets", async () => {
  const err = new Error("Vercel Blob: This store is blocked. token=vercel_blob_rw_SECRET");
  assert.equal(storeErrorReason(err), "store-blocked");
  const res = storeUnavailableResponse(err);
  assert.equal(res.status, 503);
  const body = await res.json();
  assert.equal(body.storeUnavailable, true);
  assert.ok(!JSON.stringify(body).includes("SECRET"));
});

test("other failures classify without leaking", () => {
  assert.equal(storeErrorReason(new Error("403 Forbidden")), "forbidden");
  assert.equal(storeErrorReason(new Error("fetch failed")), "network");
  assert.equal(storeErrorReason("weird"), "read-failed");
});
