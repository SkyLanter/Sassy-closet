import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { categoryFilterLabel } from "../lib/categories";
import { TYPE_LABELS } from "../lib/catalog";
import { hostnameOfImageSrc, remoteImageAllowed, shouldOptimizeImage } from "../lib/image-hosts";
import { MA_LETTERS } from "../lib/ma";

/** Hosts seen on the live 62-mã catalog, plus the Alicdn sibling named in review. */
const LIVE_CATALOG_IMAGE_URLS = [
  "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/products/A01/cover.jpg?v=1",
  "https://img.alicdn.com/imgextra/i3/1867008789/O1CN01MS07NO2EnPyOJiVCy_!!1867008789.png",
  "https://gw.alicdn.com/imgextra/i1/example.jpg",
  "https://litter.catbox.moe/c1oow8.jpg",
  "https://files.catbox.moe/abc.jpg",
];

test("filter chips use the same English names as the menu", () => {
  for (const letter of MA_LETTERS) {
    assert.equal(categoryFilterLabel(letter), TYPE_LABELS[letter].nav);
  }
});

test("every catalog image host is allowed", () => {
  const root = process.cwd();
  const config = readFileSync(path.join(root, "next.config.ts"), "utf8");
  assert.match(config, /SHOP_REMOTE_IMAGE_PATTERNS/);

  const doc = JSON.parse(readFileSync(path.join(root, "data/products.json"), "utf8")) as {
    products: Array<{ ma: string; images?: Array<{ src?: string } | string> }>;
  };
  assert.ok(doc.products.length > 0);

  for (const product of doc.products) {
    for (const image of product.images ?? []) {
      const src = typeof image === "string" ? image : (image.src ?? "");
      const host = hostnameOfImageSrc(src);
      if (host) {
        assert.equal(remoteImageAllowed(src), true, `${product.ma} host ${host} is not allowed`);
      } else {
        assert.equal(src.startsWith("/"), true, `${product.ma} image is not a local path: ${src}`);
        assert.equal(shouldOptimizeImage(src), true);
      }
    }
  }

  for (const src of LIVE_CATALOG_IMAGE_URLS) {
    assert.equal(remoteImageAllowed(src), true, src);
  }

  assert.equal(remoteImageAllowed("https://evil.example/a.jpg"), false);
  assert.equal(shouldOptimizeImage("https://evil.example/a.jpg"), false);
  assert.equal(shouldOptimizeImage("/products/A15/cover.jpg?v=1"), true);
});
