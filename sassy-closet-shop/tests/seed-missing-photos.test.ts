import assert from "node:assert/strict";
import test from "node:test";
import { productJsonLd } from "../lib/seo";
import { toShopLook } from "../lib/shop-look";

test("seed catalog read drops local photos that are not in the build manifest", async () => {
  const saved: Record<string, string | undefined> = {};
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL/.test(key)) {
      saved[key] = process.env[key];
      delete process.env[key];
    }
  }
  try {
    const { invalidateLiveCatalogMemo, readLiveCatalogRecord } = await import("../lib/catalog-store");
    invalidateLiveCatalogMemo();
    const record = await readLiveCatalogRecord();
    assert.equal(record.source, "seed");
    const s03 = record.document.products.find((product) => product.ma === "S03");
    assert.ok(s03);
    const srcs = s03.images.map((image) => image.src.split("?")[0]);
    assert.equal(srcs.includes("/products/S03/cover.jpg"), true);
    assert.equal(srcs.includes("/products/S03/photo-2.jpg"), false);
    assert.equal(srcs.includes("/products/S03/photo-3.jpg"), false);
    const html = JSON.stringify(productJsonLd(toShopLook(s03)));
    assert.equal(html.includes("/products/S03/cover.jpg"), true);
    assert.equal(html.includes("photo-2.jpg"), false);
    assert.equal(html.includes("photo-3.jpg"), false);
  } finally {
    const { invalidateLiveCatalogMemo } = await import("../lib/catalog-store");
    invalidateLiveCatalogMemo();
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  }
});
