// Piece 201: call sites of lib/ma.ts normalizeMa that guard a check must treat
// padded / spaced / lower / short spellings like the canonical mã. Fake in-memory data.
import assert from "node:assert/strict";
import test from "node:test";
import { inspectCatalogIntegrity } from "../lib/catalog-integrity";
import { KNOWN_SEED_MAS } from "../lib/catalog-contract";
import { hubColorLocked } from "../lib/hub-colors";
import { canonicalMaSpelling } from "../lib/ma";
import type { Product } from "../lib/types";

function variants(ma: string): string[] {
  const letter = ma[0];
  const n = Number(ma.slice(1));
  return [ma, ` ${ma} `, ma.toLowerCase(), `${letter}0${ma.slice(1)}`, `${letter}${n}`, ` ${letter.toLowerCase()}${n} `];
}

test("hubColorLocked: every spelling of a hub mã stays locked", () => {
  for (const hub of KNOWN_SEED_MAS) {
    for (const v of variants(hub)) {
      assert.equal(hubColorLocked(v), hubColorLocked(canonicalMaSpelling(v)), `${JSON.stringify(v)}`);
      assert.equal(hubColorLocked(v), true, `${JSON.stringify(v)} must be locked`);
    }
  }
  for (const v of variants("A93")) assert.equal(hubColorLocked(v), false);
});

test("inspectCatalogIntegrity: padded/short twin of a mã is reported as a duplicate", () => {
  const row = (ma: string) => ({ ma, status: "available", priceUsd: 10 }) as unknown as Product;
  for (const base of ["K93", "A01"]) {
    for (const v of variants(base).slice(1)) {
      const report = inspectCatalogIntegrity([row(base), row(v)]);
      assert.deepEqual(report.duplicates, [base], `${base} + ${JSON.stringify(v)}`);
    }
    assert.deepEqual(inspectCatalogIntegrity([row(base)]).duplicates, []);
  }
});
