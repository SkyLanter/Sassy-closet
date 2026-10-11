import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import held from "../../data/held.json";
import { HELD_INCOMPLETE_MAS, isHeldIncompleteMa } from "../lib/held-incomplete";

const LIST_LINE = held.heldIncomplete.join(", ");

const LIST_FILES = [
  "docs/SHOP_ADMIN.md",
  "BOSS.md",
  "README.md",
  "../README.md",
  ".env.example",
  "../sassy-closet-shop/README.md",
] as const;

test("held incomplete config loads data/held.json, including K06 and V05", () => {
  assert.deepEqual([...HELD_INCOMPLETE_MAS], [...held.heldIncomplete]);
  assert.ok(HELD_INCOMPLETE_MAS.includes("K06"));
  assert.ok(HELD_INCOMPLETE_MAS.includes("V05"));
  assert.equal(isHeldIncompleteMa("s15"), true);
  assert.equal(isHeldIncompleteMa("A26"), true);
  assert.equal(isHeldIncompleteMa("K02"), true);
  assert.equal(isHeldIncompleteMa("K03"), true);
  assert.equal(isHeldIncompleteMa("k04"), true);
  assert.equal(isHeldIncompleteMa("K05"), true);
  assert.equal(isHeldIncompleteMa("V04"), true);
  assert.equal(isHeldIncompleteMa("K06"), true);
  assert.equal(isHeldIncompleteMa("v05"), true);
  assert.equal(isHeldIncompleteMa("S06"), false);
  assert.equal(isHeldIncompleteMa("Q02"), false);
  assert.equal(isHeldIncompleteMa("A07"), false);
  assert.equal(isHeldIncompleteMa("S10"), false);
  const source = readFileSync(new URL("../lib/held-incomplete.ts", import.meta.url), "utf8");
  assert.match(source, /data\/held\.json/);
  assert.equal(source.includes('["S14"'), false);
});

test("docs and config lists enumerate every held incomplete mã", () => {
  for (const rel of LIST_FILES) {
    const text = readFileSync(new URL(`../${rel}`, import.meta.url), "utf8");
    assert.ok(text.includes(LIST_LINE), `${rel} is missing ${LIST_LINE}`);
  }
});
