import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";

const SECRET = "catalog-src-must-not-escape-public";

test("product image route does not read outside public when a catalog src uses ..", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "shop-img-"));
  const cwd = process.cwd();
  const saved: Record<string, string | undefined> = {};
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL/.test(key)) {
      saved[key] = process.env[key];
      delete process.env[key];
    }
  }
  try {
    fs.mkdirSync(path.join(tmp, "data"), { recursive: true });
    fs.mkdirSync(path.join(tmp, "public", "products", "Q02"), { recursive: true });
    fs.writeFileSync(path.join(tmp, "secret.txt"), SECRET);
    fs.writeFileSync(path.join(tmp, "public", "products", "Q02", "photo-2.jpg"), "real-photo");
    const product = {
      ma: "Q02",
      type: "Q",
      titleVn: "Q02",
      titleEn: "Q02",
      priceUsd: 20,
      qty: 1,
      status: "available",
      colors: [],
      images: [{ src: "/../secret.txt", colorId: null, order: 1 }],
      sizes: [],
      fitCm: emptyFitCm(),
      descriptionVn: "",
      descriptionEn: "",
      fulfillment: "dropship",
      sourceLink: null,
    };
    fs.writeFileSync(path.join(tmp, "data", "live-catalog.json"), JSON.stringify([product]));
    process.chdir(tmp);
    const { invalidateLiveCatalogMemo } = await import("../lib/catalog-store");
    invalidateLiveCatalogMemo();
    const { GET } = await import("../app/products/[ma]/[file]/route");
    const call = (file: string) =>
      GET(new Request(`https://example.invalid/products/Q02/${file}`), {
        params: Promise.resolve({ ma: "Q02", file }),
      });
    const photo = await call("photo-2.jpg");
    assert.equal(photo.status, 200);
    assert.equal(await photo.text(), "real-photo");
    const cover = await call("cover.jpg");
    const body = await cover.text();
    assert.equal(body.includes(SECRET), false);
    assert.equal(cover.status, 404);
    assert.match(cover.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
  } finally {
    process.chdir(cwd);
    const { invalidateLiveCatalogMemo } = await import("../lib/catalog-store");
    invalidateLiveCatalogMemo();
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
