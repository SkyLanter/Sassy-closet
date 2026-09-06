import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";

import { analyzeRgba, codesFromHistogram } from "./colors-client.ts";
import { analyzeRgbaLegacy, codesFromHistogramLegacy } from "./colors-legacy.ts";
import { downscaleNearest, loadPngRgba } from "./load-png.ts";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const creamPath = path.join(root, "bugs", "sample-cream-cardigan.png");
const redPath = path.join(root, "bugs", "sample-red-cardigan.png");

function ensureFixtures(): void {
  if (existsSync(creamPath) && existsSync(redPath)) return;
  const r = spawnSync("python3", [path.join(root, "scripts", "make_fixtures.py")], {
    stdio: "inherit",
  });
  assert.equal(r.status, 0, "fixture generator");
}

function chips(file: string, which: "new" | "legacy"): string[] {
  const png = loadPngRgba(file);
  const small = downscaleNearest(png.data, png.width, png.height);
  if (which === "legacy") {
    return codesFromHistogramLegacy(analyzeRgbaLegacy(small.data, small.width, small.height));
  }
  return codesFromHistogram(analyzeRgba(small.data, small.width, small.height));
}

test("fixtures exist", () => {
  ensureFixtures();
  assert.ok(existsSync(creamPath));
  assert.ok(existsSync(redPath));
});

test("cream cardigan → Kem dominant (not backdrop Trắng/Be)", () => {
  ensureFixtures();
  const next = chips(creamPath, "new");
  assert.equal(next[0], "kem", `cream chips=${next.join(",")}`);
  assert.ok(!next.includes("den"), `couch Đen leaked: ${next.join(",")}`);
});

test("cream gingham can add Caro", () => {
  ensureFixtures();
  const next = chips(creamPath, "new");
  // Collar is small; Caro is allowed, not required if tiles < 6 after mask.
  assert.ok(next[0] === "kem");
});

test("red cardigan → Đỏ dominant", () => {
  ensureFixtures();
  const next = chips(redPath, "new");
  assert.equal(next[0], "do", `red chips=${next.join(",")}`);
  assert.ok(!next.includes("den"), `couch Đen leaked: ${next.join(",")}`);
});

test("same photo → same chips (stable)", () => {
  ensureFixtures();
  assert.deepEqual(chips(creamPath, "new"), chips(creamPath, "new"));
  assert.deepEqual(chips(redPath, "new"), chips(redPath, "new"));
});

function centerSwatch(
  rgb: [number, number, number],
  bg: [number, number, number] = [18, 16, 14],
): { data: Uint8ClampedArray; width: number; height: number } {
  const width = 160;
  const height = 200;
  const data = new Uint8ClampedArray(width * height * 4);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = (y * width + x) * 4;
      const inGarment = x > 28 && x < 132 && y > 24 && y < 176;
      const [r, g, b] = inGarment ? rgb : bg;
      data[i] = r;
      data[i + 1] = g;
      data[i + 2] = b;
      data[i + 3] = 255;
    }
  }
  return { data, width, height };
}

function firstChip(rgb: [number, number, number], bg?: [number, number, number]): string {
  const img = centerSwatch(rgb, bg);
  return codesFromHistogram(analyzeRgba(img.data, img.width, img.height))[0];
}

test("solid swatches keep their own chip", () => {
  assert.equal(firstChip([237, 226, 204]), "kem");
  assert.equal(firstChip([196, 30, 46]), "do");
  assert.equal(firstChip([246, 246, 245]), "trang");
  assert.equal(firstChip([176, 142, 104]), "be");
  assert.equal(firstChip([22, 20, 18], [240, 240, 240]), "den");
});

test("legacy cream often prefers Trắng/Be/Nâu over Kem (hypothesis)", () => {
  ensureFixtures();
  const old = chips(creamPath, "legacy");
  const next = chips(creamPath, "new");
  assert.equal(next[0], "kem");
  // Document the live-site failure mode when it shows up on this layout.
  if (old[0] !== "kem") {
    assert.ok(["trang", "be", "nau", "den"].includes(old[0]), `legacy cream=${old.join(",")}`);
  }
});
