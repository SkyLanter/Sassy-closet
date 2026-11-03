import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import held from "../../data/held.json";
import { HELD_INCOMPLETE_MAS, NEVER_LIST_MAS } from "../lib/held-incomplete";

const APP_ROOT = process.cwd();
const SCAN_DIRS = ["scripts", "tests", "lib", "app", "components"];
const SKIP = new Set(["node_modules", ".next"]);
const HELD = new Set([...held.heldIncomplete, ...held.neverList].map((ma) => ma.toUpperCase()));
const MA_LITERAL = /["'`]([A-Z]\d{2})["'`]/g;
/**
 * An array made only of mã string literals that names three or more held mãs
 * means someone re-typed the held list. A fixture that genuinely needs such an
 * array (e.g. every K mã for minting) marks its line with "held-list-ok:".
 */
const ARRAY_LITERAL = /\[\s*(?:["'`][A-Z]\d{2}["'`]\s*,?\s*){3,}\][^\n]*/g;

function walk(dir: string, out: string[]): string[] {
  for (const name of readdirSync(dir)) {
    if (SKIP.has(name)) continue;
    const full = path.join(dir, name);
    if (statSync(full).isDirectory()) walk(full, out);
    else if (/\.(ts|tsx|mjs|cjs|js)$/.test(name)) out.push(full);
  }
  return out;
}

function hardCodedHeldLists(source: string, heldSet: ReadonlySet<string>): string[][] {
  const hits: string[][] = [];
  for (const block of source.match(ARRAY_LITERAL) ?? []) {
    if (block.includes("held-list-ok:")) continue;
    const mas = [...block.matchAll(MA_LITERAL)].map((m) => m[1]).filter((ma) => heldSet.has(ma));
    const total = [...block.matchAll(MA_LITERAL)].length;
    const distinct = new Set(mas).size;
    // Mostly-held arrays are re-typed held lists; a long mixed list (e.g. trap tiles) is not.
    if (distinct >= 3 && distinct / total >= 0.75) hits.push(mas);
  }
  return hits;
}

test("loader matches data/held.json exactly", () => {
  assert.deepEqual([...HELD_INCOMPLETE_MAS], [...held.heldIncomplete]);
  assert.deepEqual([...NEVER_LIST_MAS], [...held.neverList]);
});

test("no sell-site script, test or lib hard-codes a held list", () => {
  const offenders: string[] = [];
  for (const dir of SCAN_DIRS) {
    let files: string[] = [];
    try {
      files = walk(path.join(APP_ROOT, dir), []);
    } catch {
      continue;
    }
    for (const file of files) {
      const hits = hardCodedHeldLists(readFileSync(file, "utf8"), HELD);
      if (hits.length) offenders.push(`${path.relative(APP_ROOT, file)}: ${hits.map((h) => h.join(",")).join(" | ")}`);
    }
  }
  assert.deepEqual(offenders, [], `Read data/held.json via lib/held-incomplete instead:\n${offenders.join("\n")}`);
});

test("detector catches a re-typed (even stale) held list", () => {
  const q = (ma: string) => `"${ma}"`;
  const stale = `const X = [${["S14", "A24"].map(q).join(", ")}, ${q("A25")}, ${q("S15")}] as const;`;
  assert.equal(hardCodedHeldLists(stale, HELD).length, 1);
  assert.equal(hardCodedHeldLists(`const Y = [${q("S14")}, ${q("Q02")}];`, HELD).length, 0);
  const mixed = ["A03", "Q01", "V01", "S14", "B01", "A24", "J01", "A25"].map(q).join(", ");
  assert.equal(hardCodedHeldLists(`const Z = [${mixed}];`, HELD).length, 0);
  assert.equal(hardCodedHeldLists(`[${q("S14")}, ${q("A24")}, ${q("A25")}] // held-list-ok: fixture`, HELD).length, 0);
});

test("smoke:seo and share-card test read the loader", () => {
  for (const rel of ["scripts/smoke-seo-trust.ts", "tests/share-card.test.ts"]) {
    const source = readFileSync(path.join(APP_ROOT, rel), "utf8");
    assert.match(source, /from "\.\.\/lib\/held-incomplete"/, rel);
    assert.match(source, /HELD_OFF_SELL: readonly string\[\] = \[\.\.\.HELD_INCOMPLETE_MAS, \.\.\.NEVER_LIST_MAS\]/, rel);
  }
});
