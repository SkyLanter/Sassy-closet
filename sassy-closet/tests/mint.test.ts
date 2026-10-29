import assert from "node:assert/strict";
import { test } from "node:test";
import { formatMa, maExists, nextMa, normalizeMa, parseHubMa } from "../lib/mint";

test("parse/format/normalize round-trip for hub mãs", () => {
  assert.deepEqual(parseHubMa(" a05 "), { kind: "A", n: 5 });
  assert.deepEqual(parseHubMa("S123"), { kind: "S", n: 123 });
  assert.equal(parseHubMa("A5"), null);
  assert.equal(parseHubMa("Z01"), null);
  assert.equal(parseHubMa("A00"), null);
  assert.equal(parseHubMa("A1000"), null);
  assert.equal(formatMa("A", 7), "A07");
  assert.equal(formatMa("A", 120), "A120");
  assert.equal(normalizeMa("a007"), "A07");
  assert.equal(normalizeMa(" x-1 "), "X-1");
});

test("nextMa is max+1 per kind, skips blocked and ignores other kinds", () => {
  assert.equal(nextMa("A", []), "A01");
  assert.equal(nextMa("A", ["A01", "A03", "S09"]), "A04");
  assert.equal(nextMa("A", ["a002"]), "A03");
  assert.equal(nextMa("S", ["S01"], ["S02", "S03"]), "S04");
});

test("nextMa past 999 throws and never reuses a gap", () => {
  const full = Array.from({ length: 999 }, (_, i) => formatMa("A", i + 1));
  assert.throws(() => nextMa("A", full), /no free mã left/i);
  const withGap = full.filter((ma) => ma !== "A10");
  assert.throws(() => nextMa("A", withGap), /gaps are never reused/i);
  assert.throws(() => nextMa("A", ["A999"]), /no free mã left/i);
  assert.equal(nextMa("A", ["A998"]), "A999");
  assert.throws(() => nextMa("A", ["A997"], ["A998", "A999"]), /no free mã left/i);
});

test("maExists matches normalized codes and honours except", () => {
  assert.ok(maExists(["A01"], "a001"));
  assert.ok(!maExists(["A01"], "A01", "a1".replace("1", "01")));
  assert.ok(!maExists(["A02"], "A01"));
});
