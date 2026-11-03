import assert from "node:assert/strict";
import test from "node:test";
import { canonicalCategoryPath, canonicalMaPath } from "../lib/ma-url";

// proxy.ts calls these on every request; a bad %-escape must not throw (500).
test("canonical path helpers ignore malformed percent escapes", () => {
  const bad = "%" + "E0%A4%A";
  for (const p of [`/m/${bad}`, `/share/m/${bad}`, `/c/${bad}`, `/share/c/${bad}`]) {
    assert.doesNotThrow(() => canonicalMaPath(p), p);
    assert.doesNotThrow(() => canonicalCategoryPath(p), p);
    assert.equal(canonicalMaPath(p), null);
    assert.equal(canonicalCategoryPath(p), null);
  }
  assert.equal(canonicalMaPath("/m/a01"), "/m/A01");
  assert.equal(canonicalCategoryPath("/c/Ao"), "/c/ao");
});
