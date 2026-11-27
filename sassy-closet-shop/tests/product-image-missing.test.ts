import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { maLetter } from "../lib/ma";

// A01/photo-2.jpg is on the build manifest, so catalog hydrate keeps the slide.
// The file is absent on disk. The public route must 404, not answer with cover.jpg.
test("missing photo-N is not served as the cover", async () => {
  const ma = "A01";
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "shop-photo-miss-"));
  const cwd = process.cwd();
  const savedEnv = { ...process.env };
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL/.test(key)) {
      delete process.env[key];
    }
  }
  try {
    fs.mkdirSync(path.join(tmp, "data"), { recursive: true });
    fs.mkdirSync(path.join(tmp, "public", "products", ma), { recursive: true });
    const cover = Buffer.from("cover-bytes-not-photo-2");
    fs.writeFileSync(path.join(tmp, "public", "products", ma, "cover.jpg"), cover);
    const product = {
      ma,
      type: maLetter(ma),
      titleVn: ma,
      titleEn: ma,
      priceUsd: 27,
      qty: 1,
      status: "available",
      colors: [],
      images: [
        { src: `/products/${ma}/cover.jpg`, colorId: null, order: 1 },
        { src: `/products/${ma}/photo-2.jpg`, colorId: null, order: 2 },
      ],
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
      GET(new Request(`https://example.invalid/products/${ma}/${file}`), {
        params: Promise.resolve({ ma, file }),
      });

    const missing = await call("photo-2.jpg");
    assert.equal(missing.status, 404);
    const missingBody = Buffer.from(await missing.arrayBuffer());
    assert.equal(missingBody.equals(cover), false);

    const coverRes = await call("cover.jpg");
    assert.equal(coverRes.status, 200);
    assert.equal(Buffer.from(await coverRes.arrayBuffer()).equals(cover), true);

    const photo = Buffer.from("real-photo-2-bytes");
    fs.writeFileSync(path.join(tmp, "public", "products", ma, "photo-2.jpg"), photo);
    const present = await call("photo-2.jpg");
    assert.equal(present.status, 200);
    assert.equal(Buffer.from(await present.arrayBuffer()).equals(photo), true);
  } finally {
    process.chdir(cwd);
    process.env = savedEnv;
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
