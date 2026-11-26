import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";

function row(ma: string, images: string[]) {
  return {
    ma,
    type: ma[0],
    titleVn: "Áo",
    titleEn: "Top",
    priceUsd: 25,
    qty: 1,
    status: "available",
    colors: [],
    images: images.map((src, index) => ({ src, colorId: null, order: index + 1 })),
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

/**
 * The shop does not publish a photo-less look, so `/m/{ma}` for that mã is a
 * placeholder page that the README keeps in admin. The sitemap must not offer
 * that URL to a crawler. Photos stay on the mãs that do list.
 */
test("the sitemap lists only mãs that have their own photo", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "shop-sitemap-"));
  const cwd = process.cwd();
  const savedEnv = { ...process.env };
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL/.test(key)) delete process.env[key];
  }
  try {
    fs.mkdirSync(path.join(tmp, "data"), { recursive: true });
    fs.writeFileSync(
      path.join(tmp, "data", "live-catalog.json"),
      JSON.stringify([
        row("A05", ["/products/A05/cover.jpg"]),
        row("A06", []),
        row("A07", ["/products/A01/cover.jpg"]),
      ]),
    );
    process.chdir(tmp);
    const { default: sitemap } = await import("../app/sitemap");
    const entries = await sitemap();
    const paths = entries.map((entry) => new URL(entry.url).pathname);
    assert.ok(paths.includes("/m/A05"), "a mã with its own photo still lists");
    assert.equal(paths.includes("/m/A06"), false, "no photo of its own");
    assert.equal(paths.includes("/m/A07"), false, "only a foreign mã's photo");
    const a05 = entries.find((entry) => new URL(entry.url).pathname === "/m/A05");
    assert.deepEqual(a05?.images, ["http://127.0.0.1:43147/products/A05/cover.jpg"]);
  } finally {
    process.chdir(cwd);
    process.env = savedEnv;
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
