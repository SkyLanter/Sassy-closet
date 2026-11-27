import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { parseCatalogDocument } from "../lib/product-parse";
import { shopSafeProduct } from "../lib/sell-contract";
import { parseSourceLink } from "../lib/source-link";

test("recorded seed Taobao links stay off the shopper payload and are not called invented", () => {
  const root = process.cwd();
  const seed = parseCatalogDocument(
    JSON.parse(readFileSync(path.join(root, "data", "products.json"), "utf8")) as unknown,
  );
  let recorded = 0;
  for (const product of seed.products) {
    if (product.sourceLink !== null) {
      const parsed = parseSourceLink(product.sourceLink, product.ma);
      assert.equal(typeof parsed, "string", product.ma);
      recorded += 1;
    }
    assert.equal(shopSafeProduct(product).sourceLink, null, product.ma);
    assert.equal(shopSafeProduct(product).priceUsd, product.priceUsd, product.ma);
  }
  assert.ok(recorded > 0);
  const smoke = readFileSync(path.join(root, "scripts", "smoke-dropship.ts"), "utf8");
  assert.equal(smoke.includes("invented a sourceLink"), false);
});
