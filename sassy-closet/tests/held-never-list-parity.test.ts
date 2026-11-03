import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { HELD_INCOMPLETE_MAS, NEVER_LIST_MAS, canonicalHeldKey, isHeldIncompleteMa } from "../lib/held-incomplete";
import { publishBlock } from "../lib/publish-guard";

// Piece 202: same vector as scripts/tests/test_held_never_list_parity.py and the shop test.
type Row = { ma: string; status: "held" | "never-list" | "none"; variants: string[] };
const root = path.join(process.cwd(), "..");
const vec = JSON.parse(fs.readFileSync(path.join(root, "scripts/testdata/held-never-list-vectors.json"), "utf8"));
const src = JSON.parse(fs.readFileSync(path.join(root, "data/held.json"), "utf8"));
const rows: Row[] = vec.rows;

test("intake loads the same held / never-list sets as data/held.json and the vector", () => {
  assert.deepEqual([...HELD_INCOMPLETE_MAS], src.heldIncomplete);
  assert.deepEqual([...NEVER_LIST_MAS], src.neverList);
  assert.deepEqual(vec.heldIncomplete, src.heldIncomplete);
  assert.deepEqual(vec.neverList, src.neverList);
});

test("every spelling gets its canonical mã's held / never-list verdict", () => {
  for (const r of rows) {
    for (const v of [r.ma, ...r.variants]) {
      assert.equal(canonicalHeldKey(v), r.ma, `canonicalHeldKey(${JSON.stringify(v)})`);
      assert.equal(isHeldIncompleteMa(v), r.status === "held", `isHeldIncompleteMa(${JSON.stringify(v)})`);
      const want = r.status === "held" ? "held" : r.status === "never-list" ? "never-list" : null;
      for (const action of ["create", "update", "mint", "sync"] as const) {
        assert.equal(publishBlock({ action, ma: v, sellUsd: "25" }), want, `${action} ${JSON.stringify(v)}`);
      }
    }
  }
});

test("S06 stays $25-locked under every spelling, and its held status matches data/held.json", () => {
  const s06 = rows.find((r) => r.ma === "S06");
  assert.ok(s06);
  assert.equal(vec.s06LockUsd, 25);
  assert.equal(s06.status === "held", src.heldIncomplete.includes("S06"));
  for (const v of [s06.ma, ...s06.variants]) {
    assert.equal(publishBlock({ action: "create", ma: v, sellUsd: "25" }), null);
    assert.equal(publishBlock({ action: "create", ma: v, sellUsd: "19" }), "s06-lock");
    assert.equal(publishBlock({ action: "update", ma: v, sellUsd: "30" }), "s06-lock");
    assert.equal(publishBlock({ action: "sync", ma: v, sellUsd: "25", sellCurrency: "CNY" }), "s06-lock");
  }
});
