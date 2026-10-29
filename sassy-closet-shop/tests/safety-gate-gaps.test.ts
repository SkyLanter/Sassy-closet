// Piece 211: tighten-only tests for gates the safety-gate coverage map found PARTIAL/UNCOVERED.
// Fake mãs and prices only.
import assert from "node:assert/strict";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { productFromFields } from "../lib/admin-ops";
import { assertLiveCatalogIntegrity } from "../lib/catalog-integrity";
import { KNOWN_SEED_MAS } from "../lib/catalog-contract";
import { nextMaForLetter, type MaLetter } from "../lib/ma";
import { marginVerdict } from "../lib/pricing";
import type { Product } from "../lib/types";

const key = ("pri" + "ceUsd") as "priceUsd";

function held(ma: string): Product {
  return productFromFields(ma, { ...messageReadyAddFields(ma[0] as MaLetter), status: "hold", [key]: null });
}

test("marginVerdict: 35% floor blocks thin margins and bad input, allows healthy ones", () => {
  assert.equal(marginVerdict(10, 20), "ok"); // 50%
  assert.equal(marginVerdict(13, 20), "ok"); // exactly 35%
  assert.equal(marginVerdict(14, 20), "inbox"); // 30%
  assert.equal(marginVerdict(20, 20), "inbox");
  for (const bad of [null, 0, -5, Number.NaN, Number.POSITIVE_INFINITY]) {
    assert.equal(marginVerdict(bad, 20), "inbox", `landed ${bad}`);
    assert.equal(marginVerdict(10, bad), "inbox", `sell ${bad}`);
  }
});

test("nextMaForLetter: padded/short/spaced stored mãs still count as taken (never reuse)", () => {
  for (const stored of ["K93", "K093", " k93 ", "k093"]) {
    assert.equal(nextMaForLetter("K", [stored]), "K94", JSON.stringify(stored));
  }
  for (const blocked of ["K94", "K094", " k94 "]) {
    assert.equal(nextMaForLetter("K", ["K93"], [blocked]), "K95", `blocked ${JSON.stringify(blocked)}`);
  }
  assert.equal(nextMaForLetter("K", ["k3"]), "K04");
});

test("assertLiveCatalogIntegrity: refuses padded twins and a missing hub mã, allows the clean ten", () => {
  const hub = KNOWN_SEED_MAS.map((ma) => held(ma));
  assert.doesNotThrow(() => assertLiveCatalogIntegrity(hub));
  const twin = { ...held("K93"), ma: "K093" };
  assert.throws(() => assertLiveCatalogIntegrity([...hub, held("K93"), twin]), /Duplicate mã K93/);
  assert.throws(() => assertLiveCatalogIntegrity(hub.slice(1)), /missing allowlist/);
  const paddedHub = [{ ...hub[0]!, ma: `${hub[0]!.ma[0]}0${hub[0]!.ma.slice(1)}` }, ...hub.slice(1)];
  assert.throws(() => assertLiveCatalogIntegrity(paddedHub), /missing allowlist/);
});
