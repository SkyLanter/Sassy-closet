import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { analyzeRgba, codesFromHistogram } from "../lib/colors-client.ts";
import { analyzeRgbaLegacy, codesFromHistogramLegacy } from "../lib/colors-legacy.ts";
import { downscaleNearest, loadPngRgba } from "../lib/load-png.ts";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");

function ensure(): void {
  const cream = path.join(root, "bugs", "sample-cream-cardigan.png");
  if (existsSync(cream)) return;
  spawnSync("python3", [path.join(root, "scripts", "make_fixtures.py")], { stdio: "inherit" });
}

function run(file: string): { next: string[]; legacy: string[] } {
  const png = loadPngRgba(file);
  const small = downscaleNearest(png.data, png.width, png.height);
  return {
    next: codesFromHistogram(analyzeRgba(small.data, small.width, small.height)),
    legacy: codesFromHistogramLegacy(analyzeRgbaLegacy(small.data, small.width, small.height)),
  };
}

ensure();
const cases = [
  ["cream", path.join(root, "bugs", "sample-cream-cardigan.png")],
  ["red", path.join(root, "bugs", "sample-red-cardigan.png")],
] as const;

for (const [name, file] of cases) {
  const { next, legacy } = run(file);
  console.log(`${name}: legacy=${legacy.join("+") || "∅"}  →  new=${next.join("+") || "∅"}`);
}
