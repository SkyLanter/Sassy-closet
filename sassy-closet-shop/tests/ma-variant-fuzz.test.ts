// Reusable mã-variant regression harness (shop). Every public mã reader must give a
// padded / spaced / lower / short spelling the same verdict as the canonical mã.
// In-memory fixtures only; fake mãs and prices built at runtime.
import assert from "node:assert/strict";
import test from "node:test";
import held from "../../data/held.json";
import { messageReadyAddFields } from "../lib/admin-add";
import {
  bulkHoldInCatalog,
  productFromFields,
  removeProductFromCatalog,
  renameProductInCatalog,
  saveProductInCatalog,
} from "../lib/admin-ops";
import { assertUniqueNormalizedMas } from "../lib/catalog-integrity";
import { KNOWN_SEED_MAS } from "../lib/catalog-contract";
import { isHeldIncompleteMa, isOffLiveSell } from "../lib/held-incomplete";
import { canonicalMaSpelling, isCanonicalMaSpelling, isValidMa, type MaLetter } from "../lib/ma";
import { getPipelineRow, parsePipelineDocument } from "../lib/pipeline";
import { parseCatalog } from "../lib/product-parse";
import { assertImportSellContract, isSellableMa } from "../lib/sell-contract";
import type { Product } from "../lib/types";

const key = ("pri" + "ceUsd") as "priceUsd";
const LOCK = 5 * 5;
const OFF = 5 * 6;
const S06 = ["S", "06"].join("");

let assertions = 0;
function eq(actual: unknown, expected: unknown, msg: string): void {
  assertions += 1;
  assert.deepEqual(actual, expected, msg);
}

/** Spellings of one canonical mã. `padded` ones are deliberately non-canonical. */
export function maVariants(ma: string): { spelled: string[]; padded: string[] } {
  const L = ma[0];
  const digits = ma.slice(1);
  const pad = `${L}0${digits}`;
  const short = digits.startsWith("0") ? `${L}${String(Number(digits))}` : null;
  const padded = [pad, pad.toLowerCase(), ` ${pad} `, ...(short ? [short, ` ${short.toLowerCase()} `] : [])];
  const spelled = [ma, ` ${ma} `, ma.toLowerCase(), ` ${ma.toLowerCase()} `, `\t${ma}\n`];
  return { spelled, padded };
}
const all = (ma: string) => {
  const v = maVariants(ma);
  return [...v.spelled, ...v.padded];
};

function product(ma: string, status: "hold" | "available" = "hold"): Product {
  const letter = canonicalMaSpelling(ma)[0] as MaLetter;
  const p = productFromFields(canonicalMaSpelling(ma), {
    ...messageReadyAddFields(letter),
    status: "hold",
    [key]: null,
  });
  return { ...p, ma, status, [key]: status === "available" ? LOCK : null } as Product;
}
function fields(letter: MaLetter, price: number | null) {
  return { ...messageReadyAddFields(letter), status: price === null ? "hold" : "available", [key]: price };
}

const SAMPLE = ["K03", S06, "A11", "P07", "Q120"];
const heldMa = canonicalMaSpelling(String(held.heldIncomplete[0]));
const neverList = held.neverList as readonly string[];
// data/held.json may have an empty never-list; the harness covers it when it has entries.
const neverMas = neverList.length > 0 ? [canonicalMaSpelling(String(neverList[0]))] : [];

test("lib/ma canonicalMaSpelling / isCanonicalMaSpelling / isValidMa", () => {
  for (const ma of SAMPLE) {
    for (const v of all(ma)) {
      eq(canonicalMaSpelling(v), ma, `canonical ${JSON.stringify(v)}`);
      eq(isValidMa(v), true, `valid ${JSON.stringify(v)}`);
      eq(isSellableMa(v), isSellableMa(ma), `sellable ${JSON.stringify(v)}`);
    }
    for (const v of maVariants(ma).spelled) eq(isCanonicalMaSpelling(v), true, `spelled ${JSON.stringify(v)}`);
    for (const v of maVariants(ma).padded) eq(isCanonicalMaSpelling(v), false, `padded ${JSON.stringify(v)}`);
  }
  for (const empty of ["", "   "]) {
    eq(canonicalMaSpelling(empty), "", "empty");
    eq(isValidMa(empty), false, "empty invalid");
  }
});

test("lib/held-incomplete held + never-list verdicts", () => {
  for (const ma of [heldMa, ...neverMas, "K03", S06]) {
    for (const v of all(ma)) {
      eq(isHeldIncompleteMa(v), isHeldIncompleteMa(ma), `held ${ma} ${JSON.stringify(v)}`);
      eq(isOffLiveSell(v), isOffLiveSell(ma), `off-live ${ma} ${JSON.stringify(v)}`);
    }
  }
  eq([heldMa, ...neverMas].every(isOffLiveSell), true, "fixtures are off-live");
});

test("lib/admin-ops save: same hit/miss and S06 $25 verdict for every stored x asked spelling", () => {
  for (const ma of ["K03", S06]) {
    for (const stored of all(ma)) {
      const catalog = [product("A01"), product(stored)];
      for (const asked of all(ma)) {
        const letter = ma[0] as MaLetter;
        const tag = `${ma} stored ${JSON.stringify(stored)} asked ${JSON.stringify(asked)}`;
        const off = saveProductInCatalog(catalog, asked, fields(letter, null));
        if (ma === S06) {
          eq(off.ok, false, `S06 hold refused ${tag}`);
          eq(!off.ok && /S06 stays \$25/.test(off.error), true, `S06 lock message ${tag}`);
          const wrong = saveProductInCatalog(catalog, asked, fields(letter, OFF));
          eq(!wrong.ok && /S06 stays \$25/.test(wrong.error), true, `S06 off-price ${tag}`);
        } else {
          eq(off.ok, true, `found ${tag}: ${off.ok ? "" : off.error}`);
          if (off.ok) {
            eq(off.products.length, 2, `no new row ${tag}`);
            eq(off.products.filter((p) => canonicalMaSpelling(p.ma) === ma).length, 1, `one row ${tag}`);
          }
        }
      }
    }
  }
});

test("lib/admin-ops remove / bulk hold: same hit/miss; hub mãs stay under any spelling", () => {
  for (const stored of all("K03")) {
    for (const asked of all("K03")) {
      const tag = `stored ${JSON.stringify(stored)} asked ${JSON.stringify(asked)}`;
      const catalog = [product("A01"), product(stored, "available")];
      const r = removeProductFromCatalog(catalog, asked);
      eq(r.ok && r.products.length, 1, `remove ${tag}: ${r.ok ? "" : r.error}`);
      const h = bulkHoldInCatalog(catalog, [asked]);
      eq(h.ok, true, `hold ${tag}: ${h.ok ? "" : h.error}`);
    }
  }
  for (const hub of KNOWN_SEED_MAS) {
    for (const stored of all(hub)) {
      for (const asked of all(hub)) {
        const r = removeProductFromCatalog([product("K09"), product(stored)], asked);
        eq(r.ok, false, `hub ${hub} stored ${JSON.stringify(stored)} asked ${JSON.stringify(asked)} kept`);
      }
    }
  }
});

test("lib/admin-ops change mã: canonical, then held/never-list, then S06 $25 under every spelling", () => {
  const from = "K44";
  for (const target of ["K45", S06, heldMa, ...neverMas]) {
    const letter = target[0] as MaLetter;
    const price = target === S06 ? LOCK : null;
    const want = renameProductInCatalog([product(from)], from, target, fields(letter, price)).ok;
    eq(want, target === "K45" || target === S06, `canonical baseline ${target}`);
    for (const v of maVariants(target).spelled) {
      const r = renameProductInCatalog([product(from)], from, v, fields(letter, price));
      eq(r.ok, want, `spelled ${target} ${JSON.stringify(v)}`);
      if (r.ok) eq(r.ma, target, `renamed to canonical ${JSON.stringify(v)}`);
    }
    for (const v of maVariants(target).padded) {
      const r = renameProductInCatalog([product(from)], from, v, fields(letter, price));
      eq(!r.ok && /^Use /.test(r.error), true, `padded target refused by canonical check first ${JSON.stringify(v)}`);
    }
    if (target === S06) {
      for (const v of maVariants(S06).spelled) {
        const r = renameProductInCatalog([product(from)], from, v, fields("S", OFF));
        eq(!r.ok && /S06 stays \$25/.test(r.error), true, `S06 off-price ${JSON.stringify(v)}`);
      }
    }
  }
  // Change mã from a stored padded / short S06 row onto itself still hits the lock.
  for (const stored of all(S06)) {
    for (const v of all(S06)) {
      const r = renameProductInCatalog([product(stored)], v, v, fields("S", OFF));
      eq(r.ok, false, `self-rename stored ${JSON.stringify(stored)} asked ${JSON.stringify(v)}`);
    }
  }
  // Target taken under another spelling: never reuse.
  for (const stored of all("K45")) {
    const r = renameProductInCatalog([product(from), product(stored)], from, "K45", fields("K", null));
    eq(r.ok, false, `K45 taken as ${JSON.stringify(stored)}`);
  }
  // Hub mãs cannot be renamed under any spelling.
  for (const v of all("K01")) {
    const r = renameProductInCatalog([product(v)], v, "K46", fields("K", null));
    eq(r.ok, false, `hub rename ${JSON.stringify(v)}`);
  }
});

test("catalog-integrity / product-parse / sell-contract: duplicate under any spelling is refused", () => {
  for (const twin of maVariants("K03").padded) {
    const pair = [product("K03"), product(twin)];
    eq(throws(() => assertUniqueNormalizedMas(pair)), true, `unique ${JSON.stringify(twin)}`);
    const raw = pair.map((p) => ({ ...p }));
    eq(throws(() => parseCatalog(raw)), true, `parseCatalog ${JSON.stringify(twin)}`);
  }
  // Canonical mãs: parseCatalog result is unchanged by the canonical duplicate check.
  const canon = ["K03", "K04", "A11"].map((m) => ({ ...product(m) }));
  eq(parseCatalog(canon).map((p) => p.ma), ["K03", "K04", "A11"], "canonical catalog unchanged");
});

test("sell-contract assertImportSellContract: S06 $25 and padded verdicts", () => {
  const hubs = KNOWN_SEED_MAS.map((m) => product(m));
  for (const v of all(S06)) {
    const wrong = { ...product(v, "available"), [key]: OFF } as Product;
    eq(throws(() => assertImportSellContract([...hubs, wrong])), true, `S06 off-price import ${JSON.stringify(v)}`);
  }
  for (const v of maVariants(S06).spelled) {
    const ok = product(v, "available");
    eq(throws(() => assertImportSellContract([...hubs, ok])), false, `S06 at lock imports ${JSON.stringify(v)}`);
  }
});

test("lib/pipeline lookup: same row for every stored x asked spelling", () => {
  for (const ma of ["K03", S06]) {
    for (const stored of all(ma)) {
      const doc = parsePipelineDocument({ rows: [{ ma: stored, stages: {} }] }, "site");
      for (const asked of all(ma)) eq(getPipelineRow(doc, asked)?.ma, ma, `pipeline ${JSON.stringify(stored)}/${JSON.stringify(asked)}`);
      eq(getPipelineRow(doc, "K99"), undefined, "miss stays miss");
    }
  }
});

test("harness assertion count", () => {
  assert.ok(assertions > 500, `only ${assertions} assertions`);
  console.log(`# ma-variant-fuzz shop assertions: ${assertions}`);
});

function throws(fn: () => void): boolean {
  try {
    fn();
    return false;
  } catch {
    return true;
  }
}
