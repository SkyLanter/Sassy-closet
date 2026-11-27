import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { isShopSize } from "../lib/asia-size";
import { parseCatalogDocument } from "../lib/product-parse";

test("stored seed sizes are shop sizes, and the PDP smoke does not call them invented", () => {
  const root = process.cwd();
  const seed = parseCatalogDocument(
    JSON.parse(readFileSync(path.join(root, "data", "products.json"), "utf8")) as unknown,
  );
  const a01 = seed.products.find((product) => product.ma === "A01");
  assert.ok(a01);
  assert.deepEqual(a01.sizes, ["S", "M", "L"]);
  for (const product of seed.products) {
    for (const size of product.sizes) {
      assert.equal(isShopSize(size), true, `${product.ma} ${size}`);
    }
    assert.equal(product.fitCm.bustChestCm, null);
    assert.equal(product.fitCm.waistCm, null);
    assert.equal(product.fitCm.lengthCm, null);
  }
  const smoke = readFileSync(path.join(root, "scripts", "smoke-pdp.ts"), "utf8");
  assert.equal(smoke.includes("invented Asia sizes"), false);
});
