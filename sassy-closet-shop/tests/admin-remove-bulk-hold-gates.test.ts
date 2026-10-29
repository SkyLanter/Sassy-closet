/** Piece 213: admin remove (hub mãs under any spelling) and bulk-hold (all-or-nothing) gates. Fake mãs only. */
import assert from "node:assert/strict";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { bulkHoldInCatalog, productFromFields, removeProductFromCatalog } from "../lib/admin-ops";
import { canonicalMaSpelling, type MaLetter } from "../lib/ma";
import type { Product } from "../lib/types";

const key = ("pri" + "ceUsd") as "priceUsd";
const LOCK = 5 * 5;
const S06 = ["S", "06"].join("");

function product(ma: string, status: "hold" | "available" = "available", price: number | null = LOCK): Product {
  const letter = canonicalMaSpelling(ma)[0] as MaLetter;
  const p = productFromFields(canonicalMaSpelling(ma), { ...messageReadyAddFields(letter), status: "hold", [key]: null });
  return { ...p, ma, status, [key]: status === "available" ? price : null } as Product;
}
const base = () => [product("A01"), product("K01"), product("K03"), product("H09"), product(S06)];
const HUB_SPELLINGS = ["K01", "K001", " K01 ", "k01", "k1", " k001 ", "\tK1\n"];

test("remove: a hub mã is refused under every spelling and the catalog is untouched", () => {
  for (const asked of HUB_SPELLINGS) {
    const catalog = base();
    const r = removeProductFromCatalog(catalog, asked);
    assert.equal(r.ok, false, `hub removed via ${JSON.stringify(asked)}`);
    if (!r.ok) assert.match(r.error, /hub mã/);
    assert.equal(catalog.length, 5);
  }
  for (const asked of ["A001", " a1 "]) {
    assert.equal(removeProductFromCatalog(base(), asked).ok, false, `hub A01 removed via ${asked}`);
  }
});

test("remove: a padded stored hub row is still refused", () => {
  const catalog = [product("A01"), product("K001"), product("K03")];
  for (const asked of ["K01", "k1", "K001"]) {
    assert.equal(removeProductFromCatalog(catalog, asked).ok, false, `stored K001 removed via ${asked}`);
  }
});

test("remove: a normal non-hub mã still removes under any spelling, and only that row", () => {
  for (const asked of ["K03", "K003", " k03 ", "k3"]) {
    const r = removeProductFromCatalog(base(), asked);
    assert.equal(r.ok, true, `K03 not removed via ${JSON.stringify(asked)}`);
    if (r.ok) {
      assert.deepEqual(r.products.map((p) => p.ma), ["A01", "K01", "H09", S06]);
    }
  }
});

test("remove: missing or blank mã is refused", () => {
  for (const asked of ["K77", "Z03", "", "   ", "HELLO", "12"]) {
    const r = removeProductFromCatalog(base(), asked);
    assert.equal(r.ok, false, `removed ${JSON.stringify(asked)}`);
  }
});

test("bulk-hold: one garbage mã in the batch refuses the whole batch", () => {
  for (const bad of ["12", "HELLO", "K-03", "", "   ", "Z03", "K77"]) {
    for (const batch of [[bad, "K03"], ["K03", bad], ["K03", bad, "H09"]]) {
      const catalog = base();
      const before = JSON.stringify(catalog);
      const r = bulkHoldInCatalog(catalog, batch);
      assert.equal(r.ok, false, `batch ${JSON.stringify(batch)} accepted`);
      assert.equal(JSON.stringify(catalog), before, "input catalog mutated");
      assert.equal("products" in r, false, "refusal must not hand back a partially held catalog");
    }
  }
  assert.equal(bulkHoldInCatalog(base(), []).ok, false);
});

test("bulk-hold: valid mãs in every spelling get held and priced off", () => {
  for (const [a, b] of [["K03", "H09"], ["K003", "h9"], [" k03 ", " H009 "], ["k3", "H09"]]) {
    const r = bulkHoldInCatalog(base(), [a, b]);
    assert.equal(r.ok, true, `${a},${b} refused`);
    if (!r.ok) continue;
    for (const ma of ["K03", "H09"]) {
      const p: Product = r.products.find((x) => canonicalMaSpelling(x.ma) === ma)!;
      assert.equal(p.status, "hold");
      assert.equal(p[key], null);
    }
    assert.equal(r.products.length, 5, "no mã added or dropped");
    assert.equal(r.products.find((x) => x.ma === "A01")!.status, "available");
  }
});

test("bulk-hold: already-held mãs stay held, and S06 keeps its $25 lock", () => {
  const held = [product("A01"), product("K03", "hold"), product("H09")];
  const r = bulkHoldInCatalog(held, ["K03", "H09"]);
  assert.equal(r.ok, true);
  if (r.ok) assert.ok(r.products.filter((p) => p.ma !== "A01").every((p) => p.status === "hold"));
  for (const s of [S06, "S006", "s6"]) {
    const catalog = base();
    const before = JSON.stringify(catalog);
    const res = bulkHoldInCatalog(catalog, ["K03", s]);
    assert.equal(res.ok, false, `S06 dropped off $25 via bulk-hold ${s}`);
    if (!res.ok) assert.match(res.error, /\$25/);
    assert.equal(JSON.stringify(catalog), before);
  }
});
