import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { productFromFields, saveProductInCatalog } from "../lib/admin-ops";
import { HELD_INCOMPLETE_MAS, NEVER_LIST_MAS, canonicalHeldKey, isHeldIncompleteMa, isOffLiveSell } from "../lib/held-incomplete";
import type { Product } from "../lib/types";

// Piece 202: same vector as scripts/tests/test_held_never_list_parity.py and the intake test.
type Row = { ma: string; status: "held" | "never-list" | "none"; variants: string[] };
const root = path.join(process.cwd(), "..");
const vec = JSON.parse(fs.readFileSync(path.join(root, "scripts/testdata/held-never-list-vectors.json"), "utf8"));
const src = JSON.parse(fs.readFileSync(path.join(root, "data/held.json"), "utf8"));
const rows: Row[] = vec.rows;

test("shop loads the same held / never-list sets as data/held.json and the vector", () => {
  assert.deepEqual([...HELD_INCOMPLETE_MAS], src.heldIncomplete);
  assert.deepEqual([...NEVER_LIST_MAS], src.neverList);
  assert.deepEqual(vec.heldIncomplete, src.heldIncomplete);
});

test("every spelling gets its canonical mã's held / off-live-sell verdict", () => {
  for (const r of rows) {
    for (const v of [r.ma, ...r.variants]) {
      assert.equal(canonicalHeldKey(v.trim()), r.ma, `canonicalHeldKey(${JSON.stringify(v)})`);
      assert.equal(isHeldIncompleteMa(v), r.status === "held", `isHeldIncompleteMa(${JSON.stringify(v)})`);
      assert.equal(isOffLiveSell(v), r.status !== "none", `isOffLiveSell(${JSON.stringify(v)})`);
    }
  }
});

test("S06 stays $25-locked on save under every spelling, and its held status matches data/held.json", () => {
  const key = ("pri" + "ceUsd") as "priceUsd";
  const s06 = rows.find((r) => r.ma === "S06");
  assert.ok(s06);
  assert.equal(vec.s06LockUsd, 25);
  assert.equal(s06.status === "held", src.heldIncomplete.includes("S06"));
  assert.equal(isOffLiveSell("S06"), s06.status !== "none");
  for (const v of [s06.ma, ...s06.variants]) {
    const stored = v.trim();
    const base = productFromFields("S06", { ...messageReadyAddFields("S"), status: "hold", [key]: null });
    const catalog = [{ ...base, ma: stored } as Product];
    const bad = saveProductInCatalog(catalog, stored, { ...messageReadyAddFields("S"), status: "available", [key]: 19 });
    assert.equal(bad.ok, false, `S06 at 19 as ${JSON.stringify(v)}`);
  }
});
