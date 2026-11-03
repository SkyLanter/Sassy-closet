// Piece 204: intake publishBlock verdicts on the shared gate-verdict fixtures (fake mãs only).
// Same fixtures as scripts/tests/test_gate_verdict_parity.py and the shop parity test.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { publishBlock } from "../lib/publish-guard";
type Expect = { skip: "held" | "never-list" | null; s06: "pass" | "fail" | "n/a" };
type Fixture = {
  id: string;
  ma?: string;
  held_index?: number;
  never_index?: number;
  spelling?: string;
  sell_usd: number;
  expect: Expect;
};
const DOC: { fixtures: Fixture[] } = JSON.parse(
  readFileSync(path.join(process.cwd(), "..", "scripts", "testdata", "gate-verdict-fixtures.json"), "utf8"),
);
const HELD: { heldIncomplete: string[]; neverList: string[] } = JSON.parse(
  readFileSync(path.join(process.cwd(), "..", "data", "held.json"), "utf8"),
);

function spell(base: string, how: string): string {
  const L = base[0];
  const d = base.slice(1);
  const short = `${L}${Number(d)}`;
  const table: Record<string, string> = {
    canonical: base,
    padded: `${L}0${d}`,
    spaced: ` ${base} `,
    lower: base.toLowerCase(),
    short,
    "short-lower": short.toLowerCase(),
    "padded-lower-spaced": ` ${L.toLowerCase()}0${d} `,
  };
  return table[how] as string;
}

function resolve(fx: Fixture): string | null {
  if (fx.ma !== undefined) return fx.ma;
  const codes = fx.held_index !== undefined ? HELD.heldIncomplete : HELD.neverList;
  const idx = (fx.held_index ?? fx.never_index) as number;
  return idx < codes.length ? spell(codes[idx] as string, fx.spelling as string) : null;
}

test("fixture file is shared and non-trivial", () => {
  assert.ok(DOC.fixtures.length >= 60);
});

for (const fx of DOC.fixtures) {
  test(`publishBlock ${fx.id}`, (t) => {
    const ma = resolve(fx);
    if (ma === null) return t.skip("held.json list has no entry at this index");
    for (const action of ["create", "update", "sync"] as const) {
      const got = publishBlock({ action, ma, sellUsd: String(fx.sell_usd) });
      const skip = got === "held" || got === "never-list" ? got : null;
      assert.equal(skip, fx.expect.skip, `${action} skip ${JSON.stringify(ma)} got ${got}`);
      if (fx.expect.s06 !== "n/a") {
        assert.equal(got === "s06-lock" ? "fail" : got === null ? "pass" : got, fx.expect.s06, `${action} s06`);
      } else {
        assert.notEqual(got, "s06-lock", `${action} non-S06 must not hit the S06 lock`);
      }
    }
  });
}
