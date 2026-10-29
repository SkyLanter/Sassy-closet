import assert from "node:assert/strict";
import test from "node:test";
import { HELD_INCOMPLETE_MAS, NEVER_LIST_MAS, isHeldIncompleteMa, isOffLiveSell } from "../lib/held-incomplete";

// Build zero-padded variants at runtime ("A24" -> "A024", " a0024 ").
function padded(ma: string, zeros: number): string {
  const letter = ma.slice(0, 1);
  const digits = ma.slice(1);
  return `${letter}${"0".repeat(zeros)}${digits}`;
}

test("zero-padded held mã is still held and off live sell", () => {
  assert.ok(HELD_INCOMPLETE_MAS.length > 0);
  for (const ma of HELD_INCOMPLETE_MAS) {
    for (const v of [padded(ma, 1), ` ${padded(ma, 2).toLowerCase()} `]) {
      assert.equal(isHeldIncompleteMa(v), true, `${v} should be held`);
      assert.equal(isOffLiveSell(v), true, `${v} should be off live sell`);
    }
  }
});

test("zero-padded never-list mã is off live sell", () => {
  for (const ma of NEVER_LIST_MAS) {
    assert.equal(isOffLiveSell(padded(ma, 1)), true, `${padded(ma, 1)} should be off live sell`);
  }
});

test("different numbers are not confused", () => {
  const first = HELD_INCOMPLETE_MAS[0]!;
  const n = Number(first.slice(1)) + 100;
  const other = `${first.slice(0, 1)}${n}`;
  if (!HELD_INCOMPLETE_MAS.includes(other) && !NEVER_LIST_MAS.includes(other)) {
    assert.equal(isOffLiveSell(other), false);
  }
});
