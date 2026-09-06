/**
 * Live-site detector (ported from sassy-closet.vercel.app bundle).
 * Kept for regression proof only — do not use in the intake UI.
 */

import type { ColorCode, ColorHistogram } from "./colors-client.ts";
import { emptyHistogram } from "./colors-client.ts";

export function analyzeRgbaLegacy(
  data: Uint8ClampedArray | Uint8Array,
  width: number,
  height: number,
): ColorHistogram {
  const hist = emptyHistogram();
  const labels = new Array<ColorCode | null>(width * height).fill(null);

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = y * width + x;
      const o = i * 4;
      if (data[o + 3] < 128) continue;
      const code = classifyLegacy(data[o], data[o + 1], data[o + 2]);
      const w = weightLegacy(x, y, width, height);
      labels[i] = code;
      if (code && w > 0) {
        hist.weights[code] += w;
        hist.total += w;
      }
    }
  }
  patternLegacy(labels, width, height, hist);
  return hist;
}

export function codesFromHistogramLegacy(hist: ColorHistogram): ColorCode[] {
  if (hist.total <= 0) return [];
  const share = new Map<ColorCode, number>();
  const body: ColorCode[] = ["den", "trang", "kem", "be", "hong", "do", "xanh", "nau", "khac"];
  for (const code of body) {
    const r = hist.weights[code] / hist.total;
    if (r > 0) share.set(code, r);
  }
  collapse(share, ["trang", "kem", "be", "nau"]);
  collapse(share, ["do", "hong"]);
  const ranked = [...share.entries()].sort((a, b) => b[1] - a[1]);
  const out: ColorCode[] = [];
  for (const [code, frac] of ranked) {
    const need = code === "den" ? 0.22 : 0.07;
    const first = out.length === 0 && code === ranked[0][0];
    if (frac < need && !(first && frac >= 0.07)) continue;
    out.push(code);
    if (out.length >= 3) break;
  }
  if (hist.caroTiles >= 6) out.push("caro");
  else if (hist.floralTiles >= 8) out.push("hoa");
  return out;
}

function classifyLegacy(r8: number, g8: number, b8: number): ColorCode | null {
  const r = r8 / 255;
  const g = g8 / 255;
  const b = b8 / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  const chroma = max - min;
  const c = 1 - Math.abs(2 * l - 1);
  const s = chroma <= 0 || c <= 0 ? 0 : Math.min(1, chroma / c);
  let h = 0;
  if (chroma > 0) {
    if (max === r) h = ((g - b) / chroma) % 6;
    else if (max === g) h = (b - r) / chroma + 2;
    else h = (r - g) / chroma + 4;
    h *= 60;
    if (h < 0) h += 360;
  }
  const warm = h >= 18 && h <= 95;
  if (l <= 0.16) return "den";
  if (chroma < 0.03) {
    if (l < 0.36) return "den";
    if (l > 0.8) return "trang";
    return null;
  }
  if (chroma < 0.1) {
    if (l >= 0.8) return warm ? "kem" : "trang";
    if (l < 0.34) return "den";
    if (l >= 0.55 && warm) return "be";
    return null;
  }
  if (h >= 345 || h < 16) {
    if (l >= 0.74 && s <= 0.85) return "hong";
    if (l <= 0.3 || s < 0.3) return "nau";
    return "do";
  }
  if (h < 45) {
    if (l >= 0.82 && s <= 0.6) return "kem";
    if (l >= 0.62 && s <= 0.45) return "be";
    if (h < 25 && s >= 0.6 && l > 0.35) return "do";
    return "nau";
  }
  if (h < 72) {
    if (l >= 0.78 && s <= 0.7) return "kem";
    if (l >= 0.55 && s <= 0.45) return "be";
    if (l < 0.5) return "nau";
    return "khac";
  }
  if (h < 300) return "xanh";
  return "hong";
}

function weightLegacy(x: number, y: number, w: number, h: number): number {
  const ox = (x + 0.5 - w / 2) / (w / 2);
  const oy = (y + 0.5 - h / 2) / (h / 2);
  const l = 1.35 - Math.sqrt(ox * ox + oy * oy);
  return l <= 0 ? 0 : l * l;
}

function collapse(share: Map<ColorCode, number>, group: ColorCode[]): void {
  let best: ColorCode | null = null;
  let bestV = 0;
  for (const code of group) {
    const v = share.get(code) ?? 0;
    if (v > bestV) {
      best = code;
      bestV = v;
    }
  }
  if (!best) return;
  for (const code of group) {
    if (code !== best && (share.get(code) ?? 0) < 0.55 * bestV) share.delete(code);
  }
}

function patternLegacy(
  labels: Array<ColorCode | null>,
  width: number,
  height: number,
  hist: ColorHistogram,
): void {
  const tile = Math.max(3, Math.round(Math.min(width, height) / 24));
  const cols = Math.floor(width / tile);
  const rows = Math.floor(height / tile);
  if (cols < 3 || rows < 3) return;
  const tiles: Array<ColorCode | null> = [];
  const colorful = new Set<ColorCode>();
  for (let ty = 0; ty < rows; ty += 1) {
    for (let tx = 0; tx < cols; tx += 1) {
      const counts = new Map<ColorCode, number>();
      let n = 0;
      for (let y = ty * tile; y < ty * tile + tile; y += 1) {
        for (let x = tx * tile; x < tx * tile + tile; x += 1) {
          const code = labels[y * width + x];
          if (!code) continue;
          counts.set(code, (counts.get(code) ?? 0) + 1);
          n += 1;
        }
      }
      let mode: ColorCode | null = null;
      let best = 0;
      for (const [code, c] of counts) {
        if (c > best) {
          mode = code;
          best = c;
        }
      }
      const pick = mode && best * 2 >= n ? mode : null;
      tiles.push(pick);
      if (pick && pick !== "den" && pick !== "trang") colorful.add(pick);
    }
  }
  let caro = 0;
  for (let ty = 0; ty < rows - 1; ty += 1) {
    for (let tx = 0; tx < cols - 1; tx += 1) {
      const a = tiles[ty * cols + tx];
      const b = tiles[ty * cols + tx + 1];
      const c = tiles[(ty + 1) * cols + tx];
      const d = tiles[(ty + 1) * cols + tx + 1];
      if (a && b && a === d && b === c && a !== b) caro += 1;
    }
  }
  hist.caroTiles = caro;
  hist.floralTiles = colorful.size >= 4 ? 8 : 0;
}
