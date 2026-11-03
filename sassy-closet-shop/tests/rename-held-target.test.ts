import assert from "node:assert/strict";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { renameProductInCatalog } from "../lib/admin-ops";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { maLetter } from "../lib/ma";
import type { Product } from "../lib/types";

// Add refuses to mint a held mã ("Cannot mint"). Change-mã must not be a side
// door that moves a piece onto a held/never-list mã.
test("change mã refuses a held target like add does", () => {
  const held = HELD_INCOMPLETE_MAS[0]!;
  const letter = maLetter(held)!;
  const from = `${letter}${"9".repeat(2)}`;
  const catalog = [{ ma: from } as Product];
  const result = renameProductInCatalog(catalog, from, held, messageReadyAddFields(letter));
  assert.equal(result.ok, false, `renamed onto held ${held}`);
});
