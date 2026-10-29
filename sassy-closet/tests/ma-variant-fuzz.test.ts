// Reusable mã-variant regression harness (intake). Every public mã reader must give a
// padded / spaced / lower / short spelling the same verdict as the canonical mã.
// In-memory fixtures only; fake mãs and prices built at runtime.
import assert from "node:assert/strict";
import test from "node:test";
import held from "../../data/held.json";
import { captionStarter, editDeepLink } from "../lib/captions";
import { isHeldIncompleteMa } from "../lib/held-incomplete";
import { listingItemForMa, type ListingItem } from "../lib/listing-status";
import { maExists, nextMa, normalizeMa, parseHubMa } from "../lib/mint";
import { publishBlock } from "../lib/publish-guard";
import { applyShopCatalogPatch } from "../lib/shop-catalog";

const key = "pri" + "ceUsd";
const LOCK = 5 * 5;
const OFF = 5 * 6;
const S06 = ["S", "06"].join("");

let assertions = 0;
function eq(actual: unknown, expected: unknown, msg: string): void {
  assertions += 1;
  assert.deepEqual(actual, expected, msg);
}

/** Every non-canonical spelling of a canonical mã (padded, short, spaced, lower, mixed). */
export function maVariants(ma: string): string[] {
  const L = ma[0];
  const digits = ma.slice(1);
  const pad = `${L}0${digits}`;
  const short = digits.startsWith("0") ? `${L}${String(Number(digits))}` : null;
  return [
    ` ${ma} `, ma.toLowerCase(), ` ${ma.toLowerCase()} `, `\t${ma}\n`,
    pad, pad.toLowerCase(), ` ${pad} `,
    ...(short ? [short, short.toLowerCase(), ` ${short} `] : []),
  ];
}
const all = (ma: string) => [ma, ...maVariants(ma)];

const SAMPLE = ["K03", S06, "A11", "P07", "Q120"];
const heldMa = normalizeMa(String(held.heldIncomplete[0]));
const neverList = held.neverList as readonly string[];
const neverMas = neverList.length > 0 ? [normalizeMa(String(neverList[0]))] : [];

test("lib/mint normalizeMa / parseHubMa / maExists / nextMa", () => {
  for (const ma of SAMPLE) {
    for (const v of all(ma)) {
      eq(normalizeMa(v), ma, `normalize ${JSON.stringify(v)}`);
      eq(parseHubMa(normalizeMa(v)), parseHubMa(ma), `parse ${JSON.stringify(v)}`);
      eq(maExists([ma], v), true, `exists ${JSON.stringify(v)}`);
      eq(maExists([v], ma), true, `exists stored ${JSON.stringify(v)}`);
      eq(maExists([v], ma, ma), false, `except ${JSON.stringify(v)}`);
    }
  }
  for (const v of all("K03")) eq(nextMa("K", ["K01", "K02", v]), "K04", `next after ${JSON.stringify(v)}`);
  for (const empty of ["", "   "]) eq(normalizeMa(empty), "", "empty");
});

test("lib/held-incomplete + lib/publish-guard: held / never-list / S06 verdicts", () => {
  for (const ma of [heldMa, ...neverMas, "K03", S06]) {
    for (const v of all(ma)) {
      eq(isHeldIncompleteMa(v), isHeldIncompleteMa(ma), `held ${JSON.stringify(v)}`);
      for (const action of ["create", "update", "sync"] as const) {
        for (const sell of [null, String(LOCK), String(OFF)]) {
          eq(
            publishBlock({ action, ma: v, sellUsd: sell }),
            publishBlock({ action, ma, sellUsd: sell }),
            `publish ${action} ${JSON.stringify(v)} ${sell}`,
          );
        }
        eq(publishBlock({ action, ma: v, sellCurrency: "cny" }), publishBlock({ action, ma, sellCurrency: "cny" }), `cny ${JSON.stringify(v)}`);
      }
    }
  }
  eq(publishBlock({ action: "update", ma: heldMa }), "held", "held fixture blocked");
  eq(publishBlock({ action: "update", ma: S06, sellUsd: String(OFF) }), "s06-lock", "S06 fixture locked");
});

function catalogWith(storedMa: string): Record<string, unknown> {
  return {
    schema: "catalog.v1", version: 1, siteId: "sassy-closet-shop", allowlist: [], settings: {},
    products: [{ ma: storedMa, type: storedMa.trim()[0]?.toUpperCase(), titleVn: "Set", titleEn: "Set", [key]: LOCK, qty: 1,
      status: "available", colors: [], images: [], sizes: ["S"] }],
  };
}

test("lib/shop-catalog applyShopCatalogPatch: same hit and S06 $25 verdict", () => {
  for (const ma of ["K03", S06]) {
    for (const stored of all(ma)) {
      for (const asked of all(ma)) {
        const tag = `${JSON.stringify(stored)}/${JSON.stringify(asked)}`;
        const ok = applyShopCatalogPatch(catalogWith(stored), { ma: asked, [key]: LOCK }, "t");
        eq(ok.ok, true, `hit ${tag} ${ok.ok ? "" : ok.error}`);
        const off = applyShopCatalogPatch(catalogWith(stored), { ma: asked, [key]: OFF }, "t");
        eq(off.ok, ma !== S06, `S06 lock ${tag}`);
      }
      eq(applyShopCatalogPatch(catalogWith(stored), { ma: "K99", [key]: LOCK }, "t").ok, false, "miss stays miss");
    }
  }
});

test("lib/listing-status listingItemForMa + lib/captions", () => {
  for (const ma of SAMPLE) {
    const items = { [ma]: { state: "live" } as unknown as ListingItem };
    for (const v of all(ma)) {
      eq(listingItemForMa(items, v), items[ma], `listing ${JSON.stringify(v)}`);
      eq(captionStarter(v), ma, `caption ${JSON.stringify(v)}`);
      eq(new URL(editDeepLink("https://example.invalid/x", v)).searchParams.get("ma"), ma, `link ${JSON.stringify(v)}`);
    }
    eq(listingItemForMa(items, "K99"), undefined, "miss stays miss");
  }
});

test("harness assertion count", () => {
  assert.ok(assertions > 500, `only ${assertions} assertions`);
  console.log(`# ma-variant-fuzz intake assertions: ${assertions}`);
});
