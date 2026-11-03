import assert from "node:assert/strict";
import test from "node:test";
import { normalizeMa } from "../lib/mint";
import { publishBlock } from "../lib/publish-guard";

// The S06 lock must hold for any spelling normalizeMa treats as S06
// (sync webhook passes stored row.ma straight through).
test("publishBlock S06 lock holds for padded / lower-case S06 spellings", () => {
  const sell = String(5 * 6);
  for (const spelling of ["S006", "s06", " S6 ", "s0006"]) {
    if (normalizeMa(spelling) !== "S06") continue;
    assert.equal(publishBlock({ action: "sync", ma: spelling, sellUsd: sell }), "s06-lock", spelling);
  }
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: String(5 * 5) }), null);
});
