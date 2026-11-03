import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { invalidateLiveCatalogMemo } from "../lib/catalog-store";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { emptyFitCm } from "../lib/asia-size";
import { maLetter } from "../lib/ma";

test("product image URLs use the canonical mã folder and still 404 a held spelling", async () => {
  const held = HELD_INCOMPLETE_MAS[0]!;
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "shop-image-ma-"));
  const cwd = process.cwd();
  const savedEnv = { ...process.env };
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL/.test(key)) delete process.env[key];
  }
  try {
    const liveDir = path.join(tmp, "public", "products", "A01");
    const heldDir = path.join(tmp, "public", "products", held);
    fs.mkdirSync(liveDir, { recursive: true });
    fs.mkdirSync(heldDir, { recursive: true });
    fs.mkdirSync(path.join(tmp, "public", "uploads"), { recursive: true });
    fs.mkdirSync(path.join(tmp, "data"), { recursive: true });
    fs.writeFileSync(path.join(liveDir, "cover.jpg"), "live-cover");
    fs.writeFileSync(path.join(heldDir, "cover.jpg"), "held-cover");
    fs.writeFileSync(path.join(tmp, "public", "uploads", "only-a99.jpg"), "catalog-cover");
    const catalogOnly = {
      ma: "A99",
      type: maLetter("A99"),
      titleVn: "A99",
      titleEn: "A99",
      priceUsd: 20,
      qty: 1,
      status: "sold",
      colors: [],
      images: [{ src: "/uploads/only-a99.jpg", alt: "A99" }],
      sizes: [],
      fitCm: emptyFitCm(),
      descriptionVn: "",
      descriptionEn: "",
      fulfillment: "dropship",
      sourceLink: null,
    };
    fs.writeFileSync(path.join(tmp, "data", "live-catalog.json"), JSON.stringify([catalogOnly]));
    process.chdir(tmp);
    invalidateLiveCatalogMemo();
    const { GET } = await import("../app/products/[ma]/[file]/route");
    const call = async (ma: string) => {
      const response = await GET(new Request(`https://example.invalid/products/${ma}/cover.jpg`), {
        params: Promise.resolve({ ma, file: "cover.jpg" }),
      });
      const body = Buffer.from(await response.arrayBuffer()).toString();
      return { status: response.status, body, cache: response.headers.get("cache-control") };
    };

    for (const spelling of ["A1", "a01", "A001"]) {
      const ok = await call(spelling);
      assert.equal(ok.status, 200, spelling);
      assert.equal(ok.body, "live-cover", spelling);
      assert.match(ok.cache ?? "", /no-store/);
    }

    const sold = await call("a99");
    assert.equal(sold.status, 200);
    assert.equal(sold.body, "catalog-cover");

    for (const spelling of [held, held.toLowerCase(), `${held[0]}0${held.slice(1)}`]) {
      const blocked = await call(spelling);
      assert.equal(blocked.status, 404, spelling);
      assert.equal(blocked.body, "Not found");
      assert.match(blocked.cache ?? "", /no-store/);
    }
  } finally {
    process.chdir(cwd);
    process.env = savedEnv;
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
