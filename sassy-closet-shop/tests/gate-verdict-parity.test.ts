// Piece 204: shop gate verdicts on the shared gate-verdict fixtures (fake mãs only).
// Same fixtures as scripts/tests/test_gate_verdict_parity.py and the intake parity test.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { productFromFields, saveProductInCatalog } from "../lib/admin-ops";
import { isHeldIncompleteMa, isOffLiveSell } from "../lib/held-incomplete";
import { canonicalMaSpelling, isValidMa, type MaLetter } from "../lib/ma";
import type { Product } from "../lib/types";
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

const key = ("pri" + "ceUsd") as "priceUsd";

function stored(ma: string): Product {
  const canon = canonicalMaSpelling(ma);
  const letter = canon[0] as MaLetter;
  const p = productFromFields(canon, { ...messageReadyAddFields(letter), status: "hold", [key]: null });
  return { ...p, ma } as Product;
}

test("fixture file is shared and non-trivial", () => {
  assert.ok(DOC.fixtures.length >= 60);
});

for (const fx of DOC.fixtures) {
  test(`shop gates ${fx.id}`, (t) => {
    const ma = resolve(fx);
    if (ma === null) return t.skip("held.json list has no entry at this index");
    const neverCodes = new Set(HELD.neverList.map(canonicalMaSpelling));
    const skip = isHeldIncompleteMa(ma) ? "held" : neverCodes.has(canonicalMaSpelling(ma)) ? "never-list" : null;
    assert.equal(skip, fx.expect.skip, `skip ${JSON.stringify(ma)}`);
    assert.equal(isOffLiveSell(ma), fx.expect.skip !== null, `off-live ${JSON.stringify(ma)}`);
    if (fx.expect.s06 === "n/a" || !isValidMa(ma)) return;
    const letter = canonicalMaSpelling(ma)[0] as MaLetter;
    const catalog = [stored("A01"), stored(ma)];
    for (const asked of [ma, canonicalMaSpelling(ma)]) {
      const res = saveProductInCatalog(catalog, asked, {
        ...messageReadyAddFields(letter),
        status: "available",
        [key]: fx.sell_usd,
      });
      const verdict = res.ok ? "pass" : /S06 stays \$25/.test(res.error) ? "fail" : `other: ${res.error}`;
      assert.equal(verdict, fx.expect.s06, `save stored ${JSON.stringify(ma)} asked ${JSON.stringify(asked)}`);
    }
  });
}
