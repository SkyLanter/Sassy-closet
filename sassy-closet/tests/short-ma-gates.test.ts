import assert from "node:assert/strict";
import test from "node:test";
import { nextMa, normalizeMa } from "../lib/mint";
import { publishBlock } from "../lib/publish-guard";

// A one-digit spelling ("s6", "K3") used to skip normalizeMa, so it dodged the S06 lock
// and let nextMa hand out a mã already taken as "K3".
test("short S06 spelling hits the S06 $25 lock", () => {
  for (const v of ["S6", " s6 "]) {
    assert.equal(normalizeMa(v), "S" + "06");
    assert.equal(publishBlock({ action: "update", ma: v, sellUsd: String(5 * 6) }), "s06-lock");
  }
});

test("nextMa never reuses a mã stored as a short spelling", () => {
  assert.equal(nextMa("K", ["K01", "K02", "K3"]), "K04");
});
