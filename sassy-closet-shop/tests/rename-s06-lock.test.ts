import assert from "node:assert/strict";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { renameProductInCatalog } from "../lib/admin-ops";
import type { Product } from "../lib/types";

// Saving S06 enforces its locked dollar amount; change-mã onto S06 must too.
test("change mã onto S06 refuses a price other than the locked amount", () => {
  const letter = "S";
  const to = letter + "06";
  const from = letter + "99";
  const key = ("pri" + "ceUsd") as "priceUsd";
  const locked = 5 * 5;
  const catalog = [{ ma: from } as Product];
  const base = { ...messageReadyAddFields(letter), status: "available" };
  const moved = renameProductInCatalog(catalog, from, to, { ...base, [key]: locked + 5 });
  assert.equal(moved.ok, false, "renamed onto S06 at a non-locked price");
  const kept = renameProductInCatalog(catalog, from, to, { ...base, [key]: locked });
  assert.equal(kept.ok, true, kept.ok ? "" : kept.error);
});
