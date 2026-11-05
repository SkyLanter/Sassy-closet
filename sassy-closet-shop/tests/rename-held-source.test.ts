import assert from "node:assert/strict";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { renameProductInCatalog } from "../lib/admin-ops";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { canonicalMaSpelling } from "../lib/ma";
import type { Product } from "../lib/types";

test("change mã refuses to leave a held code", () => {
  const held = HELD_INCOMPLETE_MAS[0];
  assert.ok(held);
  const catalog = [{ ma: held } as Product];
  const result = renameProductInCatalog(catalog, held, "A77", messageReadyAddFields("A"));
  assert.equal(result.ok, false);
  if (!result.ok) {
    assert.match(result.error, /Cannot change mã from/);
    assert.match(result.error, new RegExp(canonicalMaSpelling(held)));
  }
  assert.equal(catalog[0]?.ma, held);

  const padded = `${held[0]}0${held.slice(1)}`;
  const spelled = renameProductInCatalog(catalog, padded, "A77", messageReadyAddFields("A"));
  assert.equal(spelled.ok, false);
  assert.equal(catalog[0]?.ma, held);
});

test("change mã refuses to leave S06 at another dollar", () => {
  const from = "S06";
  const to = "A77";
  const key = ("pri" + "ceUsd") as "priceUsd";
  const locked = 5 * 5;
  const catalog = [{ ma: from } as Product];
  const base = { ...messageReadyAddFields("A"), status: "available" as const };
  const moved = renameProductInCatalog(catalog, from, to, { ...base, [key]: locked + 5 });
  assert.equal(moved.ok, false);
  if (!moved.ok) assert.match(moved.error, /S06 stays \$25/);
  assert.equal(catalog[0]?.ma, from);

  const kept = renameProductInCatalog(catalog, "S6", to, { ...base, [key]: locked });
  assert.equal(kept.ok, true, kept.ok ? "" : kept.error);
  if (kept.ok) assert.equal(kept.ma, to);
});

test("change mã still moves an ordinary code", () => {
  const catalog = [{ ma: "A04" } as Product];
  const result = renameProductInCatalog(catalog, "A04", "A05", messageReadyAddFields("A"));
  assert.equal(result.ok, true, result.ok ? "" : result.error);
  if (result.ok) assert.equal(result.products[0]?.ma, "A05");
});
