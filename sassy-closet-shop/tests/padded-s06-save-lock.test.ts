import assert from "node:assert/strict";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { productFromFields, renameProductInCatalog, saveProductInCatalog } from "../lib/admin-ops";
import type { Product } from "../lib/types";

// A stored padded S06 row ("S006") used to skip the S06 $25 lock on save / self change-mã.
test("stored padded S06 row still hits the S06 $25 lock", () => {
  const key = ("pri" + "ceUsd") as "priceUsd";
  const padded = "S" + "006";
  const base = productFromFields("S" + "06", { ...messageReadyAddFields("S"), status: "hold", [key]: null });
  const catalog = [{ ...base, ma: padded } as Product];
  const input = { ...messageReadyAddFields("S"), status: "available", [key]: 5 * 6 };
  const saved = saveProductInCatalog(catalog, padded, input);
  assert.equal(saved.ok, false);
  const self = renameProductInCatalog(catalog, padded, padded, input);
  assert.equal(self.ok, false);
});

test("save / remove find a canonical row under a padded or lower-case spelling", () => {
  const key = ("pri" + "ceUsd") as "priceUsd";
  const ma = "K" + "03";
  const row = productFromFields(ma, { ...messageReadyAddFields("K"), status: "hold", [key]: null });
  const r = saveProductInCatalog([row], "k003", { ...messageReadyAddFields("K"), status: "hold", [key]: null });
  assert.equal(r.ok && r.products[0]?.ma, ma);
});
