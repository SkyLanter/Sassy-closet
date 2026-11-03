import assert from "node:assert/strict";
import test from "node:test";
import { HELD_INCOMPLETE_MAS, isHeldIncompleteMa } from "../lib/held-incomplete";

// Build zero-padded variants at runtime ("A24" -> "A024", " a0024 ").
function padded(ma: string, zeros: number): string {
  const letter = ma.slice(0, 1);
  const digits = ma.slice(1);
  return `${letter}${"0".repeat(zeros)}${digits}`;
}

test("zero-padded held mã is still held (intake)", () => {
  assert.ok(HELD_INCOMPLETE_MAS.length > 0);
  for (const ma of HELD_INCOMPLETE_MAS) {
    for (const v of [padded(ma, 1), ` ${padded(ma, 2).toLowerCase()} `]) {
      assert.equal(isHeldIncompleteMa(v), true, `${v} should be held`);
    }
  }
});
