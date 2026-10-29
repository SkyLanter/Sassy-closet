import assert from "node:assert/strict";
import test from "node:test";
import { prefillToDraft } from "../lib/intake-import";
import { consumeIntakePrefill } from "../lib/intake-prefill";

// /admin/new runs prefillToDraft(consumeIntakePrefill()) in a useState initializer.
// A partial/stale sessionStorage value must not crash the Add page.
function withSession(value: string, run: () => void) {
  const store = new Map([["sassy:intake-prefill:v1", value]]);
  const g = globalThis as unknown as { window?: unknown };
  g.window = {
    sessionStorage: {
      getItem: (k: string) => store.get(k) ?? null,
      removeItem: (k: string) => void store.delete(k),
    },
  };
  try {
    run();
  } finally {
    delete g.window;
  }
}

test("corrupt intake prefill in sessionStorage never crashes the Add draft", () => {
  const cases = [
    JSON.stringify({ intakeMa: "A01" }),
    JSON.stringify({ intakeMa: "A01", colors: "red", sizes: {}, captionVi: 5 }),
    JSON.stringify({ intakeMa: "A01", colors: [null, { name: 3 }], sizes: [null] }),
  ];
  for (const raw of cases) {
    withSession(raw, () => {
      const prefill = consumeIntakePrefill();
      if (prefill) {
        assert.doesNotThrow(() => prefillToDraft(prefill), raw);
        const draft = prefillToDraft(prefill);
        assert.equal(typeof draft.descriptionVn, "string");
        assert.equal(typeof draft.sourceLink, "string");
        assert.ok(Array.isArray(draft.sizes));
      }
    });
  }
});
