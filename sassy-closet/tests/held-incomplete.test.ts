import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { HELD_INCOMPLETE_MAS, isHeldIncompleteMa, isUnlistedMa, UNLISTED_MAS } from "../lib/held-incomplete";

const EXPECTED = ["S14", "A24", "A25", "S15", "A26", "K02", "K03", "K04", "K05", "V04"] as const;
const LIST_LINE = EXPECTED.join(", ");

const LIST_FILES = [
  "docs/SHOP_ADMIN.md",
  "BOSS.md",
  "README.md",
  "../README.md",
  ".env.example",
  "../sassy-closet-shop/README.md",
] as const;

test("held incomplete config names all ten unfinished mãs", () => {
  assert.deepEqual([...HELD_INCOMPLETE_MAS], [...EXPECTED]);
  assert.equal(isHeldIncompleteMa("s15"), true);
  assert.equal(isHeldIncompleteMa("A26"), true);
  assert.equal(isHeldIncompleteMa("K02"), true);
  assert.equal(isHeldIncompleteMa("K03"), true);
  assert.equal(isHeldIncompleteMa("k04"), true);
  assert.equal(isHeldIncompleteMa("K05"), true);
  assert.equal(isHeldIncompleteMa("V04"), true);
  assert.equal(isHeldIncompleteMa("S06"), false);
  assert.equal(isHeldIncompleteMa("Q02"), false);
  assert.deepEqual([...UNLISTED_MAS], ["Q02"]);
  assert.equal(isUnlistedMa("Q02"), true);
  assert.equal(isUnlistedMa("q02"), true);
  assert.equal(isUnlistedMa("S06"), false);
  for (const ma of EXPECTED) assert.equal(isUnlistedMa(ma), false);
});

test("docs and config lists enumerate every held incomplete mã", () => {
  for (const rel of LIST_FILES) {
    const text = readFileSync(new URL(`../${rel}`, import.meta.url), "utf8");
    assert.ok(text.includes(LIST_LINE), `${rel} is missing ${LIST_LINE}`);
  }
});
