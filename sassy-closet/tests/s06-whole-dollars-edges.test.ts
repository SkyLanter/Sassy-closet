import assert from "node:assert/strict";
import test from "node:test";
import { publishBlock, wholeDollars } from "../lib/publish-guard";

test("wholeDollars treats blank as empty and folds only real whole dollars", () => {
  assert.equal(wholeDollars(null), null);
  assert.equal(wholeDollars(""), null);
  assert.equal(wholeDollars("   "), null);

  for (const raw of ["25", "25.00", "$25", "２５", "\uFEFF25"]) {
    assert.equal(wholeDollars(raw), 25, raw);
  }

  for (const raw of ["25.50", "2,5", "¥25", "1e2"]) {
    assert.equal(Number.isNaN(wholeDollars(raw)), true, raw);
  }
});

test("S06 publishBlock locks a European 2,5 and still passes $25, fullwidth 25, and blank", () => {
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "2,5" }), "s06-lock");
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "$25" }), null);
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "２５" }), null);
  assert.equal(publishBlock({ action: "update", ma: "S06", sellUsd: "" }), null);
  assert.equal(
    publishBlock({ action: "sync", ma: "S06", sellUsd: "25", sellCurrency: "CNY" }),
    "s06-lock",
  );
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "$24" }), "s06-lock");
  assert.equal(publishBlock({ action: "sync", ma: "S06", sellUsd: "25.50" }), "s06-lock");
});
