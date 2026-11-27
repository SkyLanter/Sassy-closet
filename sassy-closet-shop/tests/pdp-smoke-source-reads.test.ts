import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";

function read(rel: string): string {
  return readFileSync(path.join(process.cwd(), rel), "utf8");
}

/**
 * `scripts/smoke-pdp.ts` reads the PDP size-chip sources into module-level
 * locals and then asserts on them. Commit f0c7b6e moved the chips out of the
 * gallery into product-options and renamed one of those locals, but a single
 * assertion kept the retired name. The script then died with a ReferenceError
 * before any size-chip check ran, so the smoke never reached its own checks.
 */
test("smoke-pdp only asserts on source locals it declares", () => {
  const source = read("scripts/smoke-pdp.ts");
  const declared = new Set(
    [...source.matchAll(/\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*[=:]/g)].map((match) => match[1]!),
  );
  assert.ok(declared.has("optionsSrc"));
  assert.ok(declared.has("sizeChips"));

  // Bare `name.includes(` only — `error.message.includes(` is a member access.
  const asserted = [...source.matchAll(/(?<![.$\w])([A-Za-z_$][\w$]*)\.includes\(/g)].map(
    (match) => match[1]!,
  );
  const missing = [...new Set(asserted)].filter((name) => !declared.has(name)).sort();
  assert.deepEqual(missing, [], `smoke-pdp asserts on undeclared locals: ${missing.join(", ")}`);
});

test("smoke-pdp checks the size chips in product-options, not the gallery", () => {
  const source = read("scripts/smoke-pdp.ts");
  assert.equal(/const gallerySrc\s*=/.test(source), false);
  assert.equal(/\bgallerySrc\b/.test(source.replace(/^\/\/.*$/gm, "")), false);
  assert.equal(source.includes('const optionsSrc = read("components/product-options.tsx")'), true);
  assert.equal(source.includes('const sizeChips = read("components/size-name-chips.tsx")'), true);

  const options = read("components/product-options.tsx");
  assert.equal(options.includes("SizeNameChips"), true);
  assert.equal(options.includes('data-testid="pdp-size-chips"'), true);
  assert.equal(options.includes("product.sizes.length > 0"), true);
  assert.equal(options.includes("ASIA_SIZE_LETTERS"), false);
  assert.equal(read("components/size-name-chips.tsx").includes("ASIA_SIZE_LETTERS"), false);
});
