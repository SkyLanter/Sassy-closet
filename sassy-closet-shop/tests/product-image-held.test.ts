import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { emptyFitCm } from "../lib/asia-size";
import { maLetter } from "../lib/ma";

// Run the public image route against a temp cwd holding a local live catalog
// with one held mã and one normal mã. Nothing outside the temp dir is touched.
test("public product image route does not serve photos of a held mã", async () => {
  const held = HELD_INCOMPLETE_MAS[0]!;
  const normal = ["Q", "02"].join("");
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "shop-159-"));
  const cwd = process.cwd();
  const savedEnv = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL/.test(k)) delete process.env[k];
  try {
    fs.mkdirSync(path.join(tmp, "data"), { recursive: true });
    fs.mkdirSync(path.join(tmp, "public", "uploads"), { recursive: true });
    const products = [held, normal].map((ma) => {
      fs.writeFileSync(path.join(tmp, "public", "uploads", `${ma}.jpg`), `img-${ma}`);
      return {
        ma, type: maLetter(ma), titleVn: ma, titleEn: ma, priceUsd: 20, qty: 1, status: "available",
        colors: [], images: [{ src: `/uploads/${ma}.jpg`, alt: ma }], sizes: [], fitCm: emptyFitCm(),
        descriptionVn: "", descriptionEn: "", fulfillment: "dropship", sourceLink: null,
      };
    });
    fs.writeFileSync(path.join(tmp, "data", "live-catalog.json"), JSON.stringify(products));
    process.chdir(tmp);
    const { GET } = await import("../app/products/[ma]/[file]/route");
    const call = (ma: string) =>
      GET(new Request(`https://example.invalid/products/${ma}/cover.jpg`), {
        params: Promise.resolve({ ma, file: "cover.jpg" }),
      });
    const ok = await call(normal);
    assert.equal(ok.status, 200, "normal mã photo should serve");
    const blocked = await call(held);
    assert.equal(blocked.status, 404, `held ${held} photo must not be served publicly`);
  } finally {
    process.chdir(cwd);
    process.env = savedEnv;
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
