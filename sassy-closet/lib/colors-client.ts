/**
 * Client-side garment color chips. Canvas only — no vision APIs.
 *
 * Used by the intake Màu row (auto-fill, no Suggest button).
 * Prefer the center garment blob; ignore studio couch / floor / paper backs.
 */

export type ColorCode =
  | "den"
  | "trang"
  | "kem"
  | "be"
  | "hong"
  | "do"
  | "xanh"
  | "nau"
  | "caro"
  | "hoa"
  | "khac";

export const COLOR_CHIPS: { code: ColorCode; vi: string; en: string }[] = [
  { code: "den", vi: "Đen", en: "Black" },
  { code: "trang", vi: "Trắng", en: "White" },
  { code: "kem", vi: "Kem", en: "Cream" },
  { code: "be", vi: "Be", en: "Beige" },
  { code: "hong", vi: "Hồng", en: "Pink" },
  { code: "do", vi: "Đỏ", en: "Red" },
  { code: "xanh", vi: "Xanh", en: "Blue/Green" },
  { code: "nau", vi: "Nâu", en: "Brown" },
  { code: "caro", vi: "Caro", en: "Plaid" },
  { code: "hoa", vi: "Hoa", en: "Floral" },
  { code: "khac", vi: "Khác", en: "Other" },
];

const BODY: ColorCode[] = ["den", "trang", "kem", "be", "hong", "do", "xanh", "nau", "khac"];
const WARM: ColorCode[] = ["trang", "kem", "be", "nau"];
const REDS: ColorCode[] = ["do", "hong"];
const MAX_EDGE = 192;

export type ColorHistogram = {
  weights: Record<ColorCode, number>;
  total: number;
  caroTiles: number;
  floralTiles: number;
};

export function emptyHistogram(): ColorHistogram {
  const weights = {} as Record<ColorCode, number>;
  for (const code of BODY) weights[code] = 0;
  return { weights, total: 0, caroTiles: 0, floralTiles: 0 };
}

export function mergeHistograms(list: ColorHistogram[]): ColorHistogram {
  const out = emptyHistogram();
  for (const h of list) {
    for (const code of BODY) out.weights[code] += h.weights[code];
    out.total += h.total;
    out.caroTiles += h.caroTiles;
    out.floralTiles += h.floralTiles;
  }
  return out;
}

/** Browser entry: blob/url → chip codes. SSR-safe (returns []). */
export async function detectColors(source: Blob | string): Promise<ColorCode[]> {
  const hist = await analyzePhoto(source);
  return hist ? codesFromHistogram(hist) : [];
}

export async function analyzePhoto(source: Blob | string): Promise<ColorHistogram | null> {
  if (typeof document === "undefined") return null;
  if (typeof createImageBitmap !== "function") return null;
  let bitmap: ImageBitmap | null = null;
  try {
    const blob = typeof source === "string" ? await (await fetch(source)).blob() : source;
    bitmap = await createImageBitmap(blob);
    const scale = Math.min(1, MAX_EDGE / Math.max(bitmap.width, bitmap.height));
    const w = Math.max(1, Math.round(bitmap.width * scale));
    const h = Math.max(1, Math.round(bitmap.height * scale));
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) return null;
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(bitmap, 0, 0, w, h);
    const img = ctx.getImageData(0, 0, w, h);
    return analyzeRgba(img.data, w, h);
  } catch {
    return null;
  } finally {
    bitmap?.close();
  }
}

export function analyzeRgba(
  data: Uint8ClampedArray | Uint8Array,
  width: number,
  height: number,
): ColorHistogram {
  const hist = emptyHistogram();
  const n = width * height;
  const labels = new Array<ColorCode | null>(n).fill(null);
  const garment = new Uint8Array(n);
  const backdrops = backdropSwatches(data, width, height);

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = y * width + x;
      const o = i * 4;
      if (data[o + 3] < 128) continue;
      const r = data[o];
      const g = data[o + 1];
      const b = data[o + 2];
      if (isBackdropPixel(x, y, width, height, r, g, b, backdrops)) continue;
      const code = classifyBody(r, g, b);
      const w = centerWeight(x, y, width, height);
      if (!code || w <= 0) continue;
      garment[i] = 1;
      labels[i] = code;
      hist.weights[code] += w;
      hist.total += w;
    }
  }

  scorePatternTiles(labels, garment, width, height, hist);
  return hist;
}

export function codesFromHistogram(hist: ColorHistogram): ColorCode[] {
  if (hist.total <= 0) return [];
  const share = {} as Record<ColorCode, number>;
  for (const code of BODY) share[code] = hist.weights[code] / hist.total;

  // Warm knit (cream) should not lose to highlight-Trắng / shadow-Be.
  promoteIfClose(share, "kem", ["trang", "be"], 0.28);
  // Saturated garments: keep Đỏ ahead of shadow-Nâu / leftover Đen.
  promoteIfClose(share, "do", ["nau", "den", "hong"], 0.38);

  collapseGroup(share, WARM);
  collapseGroup(share, REDS);

  const ranked = BODY.map((code) => [code, share[code]] as const)
    .filter(([, v]) => v > 0)
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));

  const out: ColorCode[] = [];
  for (const [code, frac] of ranked) {
    const need = code === "den" ? 0.22 : 0.07;
    const first = out.length === 0;
    if (frac < need && !(first && frac >= 0.07)) continue;
    out.push(code);
    if (out.length >= 3) break;
  }

  if (hist.caroTiles >= 4 && !out.includes("caro")) out.push("caro");
  else if (hist.floralTiles >= 8 && !out.includes("hoa")) out.push("hoa");
  return out;
}

type Rgb = [number, number, number];

type BackdropModel = {
  swatches: Rgb[];
  darkStudio: boolean;
  lightStudio: boolean;
  woodFloor: boolean;
  border: number;
};

function backdropSwatches(
  data: Uint8ClampedArray | Uint8Array,
  width: number,
  height: number,
): BackdropModel {
  const border = Math.max(2, Math.round(Math.min(width, height) * 0.08));
  const buckets = new Map<number, { count: number; r: number; g: number; b: number }>();
  let dark = 0;
  let light = 0;
  let wood = 0;
  let borderN = 0;

  const add = (x: number, y: number) => {
    const o = (y * width + x) * 4;
    if (data[o + 3] < 128) return;
    const r = data[o];
    const g = data[o + 1];
    const b = data[o + 2];
    const { l, s, h } = hsl(r, g, b);
    borderN += 1;
    if (l < 0.2) dark += 1;
    if (l > 0.86 && s < 0.12) light += 1;
    if (isWoodLike(h, s, l)) wood += 1;
    const key = ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4);
    const cur = buckets.get(key);
    if (cur) {
      cur.count += 1;
      cur.r += r;
      cur.g += g;
      cur.b += b;
    } else {
      buckets.set(key, { count: 1, r, g, b });
    }
  };

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (x < border || y < border || x >= width - border || y >= height - border) add(x, y);
    }
  }

  const swatches: Rgb[] = [...buckets.values()]
    .filter((b) => borderN && b.count / borderN >= 0.06)
    .sort((a, b) => b.count - a.count)
    .slice(0, 3)
    .map((b) => [b.r / b.count, b.g / b.count, b.b / b.count]);

  return {
    swatches,
    darkStudio: borderN > 0 && dark / borderN >= 0.28,
    lightStudio: borderN > 0 && light / borderN >= 0.35,
    woodFloor: borderN > 0 && wood / borderN >= 0.08,
    border,
  };
}

function isBackdropPixel(
  x: number,
  y: number,
  width: number,
  height: number,
  r: number,
  g: number,
  b: number,
  model: BackdropModel,
): boolean {
  const nx = (x + 0.5) / width - 0.5;
  const ny = (y + 0.5) / height - 0.5;
  const dist = Math.sqrt(nx * nx + ny * ny);
  const { l, s, h } = hsl(r, g, b);
  const bottom = y >= height * 0.88;
  const edge =
    x < model.border ||
    y < model.border ||
    x >= width - model.border ||
    y >= height - model.border;

  let nearSwatch = false;
  for (const [br, bg, bb] of model.swatches) {
    if (rgbDist(r, g, b, br, bg, bb) < 38) {
      nearSwatch = true;
      break;
    }
  }

  if (nearSwatch && dist > 0.22) return true;
  if (model.darkStudio && l < 0.2 && dist > 0.2) return true;
  if (model.lightStudio && l > 0.88 && s < 0.1 && dist > 0.28) return true;
  if (model.woodFloor && bottom && isWoodLike(h, s, l)) return true;
  if (edge && nearSwatch) return true;
  return false;
}

function isWoodLike(h: number, s: number, l: number): boolean {
  return h >= 18 && h <= 55 && s >= 0.12 && s <= 0.65 && l >= 0.28 && l <= 0.72;
}

function classifyBody(r: number, g: number, b: number): ColorCode | null {
  const { h, s, l, chroma } = hsl(r, g, b);
  const warm = isWarmHue(h, s, chroma);

  if (l <= 0.17) return "den";
  if (l <= 0.26 && s < 0.14) return "den";

  // Paper-white / highlight: ignore tiny hue noise.
  if (l >= 0.88 && chroma < 0.035 && s < 0.1) return "trang";

  // Soft neutrals — cream knits (incl. cable shadows) stay Kem, not Be/Trắng.
  if (chroma < 0.16 || s < 0.32) {
    if (l >= 0.9 && s < 0.05 && !warm) return "trang";
    if (l >= 0.66 && warm) {
      if (l < 0.7 && s >= 0.28) return "be";
      return "kem";
    }
    if (l >= 0.88 && s < 0.07) return "trang";
    if (l < 0.36 && s < 0.16) return "den";
    if (l >= 0.45 && l < 0.66 && warm && s >= 0.12) return "be";
  }

  if (h >= 345 || h < 16) {
    if (l >= 0.74 && s <= 0.78) return "hong";
    if (s < 0.2 && l < 0.42) return "nau";
    return "do";
  }
  if (h < 45) {
    if (l >= 0.66 && s <= 0.58) return "kem";
    if (l >= 0.5 && s <= 0.45) return "be";
    if (h < 22 && s >= 0.5 && l > 0.28) return "do";
    return "nau";
  }
  if (h < 72) {
    if (l >= 0.66 && s <= 0.7) return "kem";
    if (l >= 0.5 && s <= 0.5) return "be";
    if (l < 0.5) return "nau";
    return "khac";
  }
  if (h < 300) return "xanh";
  return "hong";
}

function isWarmHue(h: number, s: number, chroma: number): boolean {
  if (s < 0.055 || chroma < 0.028) return false;
  return (h >= 14 && h <= 78) || (h >= 8 && h <= 92 && s < 0.22);
}

function centerWeight(x: number, y: number, width: number, height: number): number {
  const ox = (x + 0.5 - width / 2) / (width / 2);
  const oy = (y + 0.5 - height / 2) / (height / 2);
  const rad = Math.sqrt(ox * ox + oy * oy);
  const raw = 1.55 - rad * 1.15;
  if (raw <= 0) return 0;
  const w = raw * raw;
  return rad < 0.42 ? w * 1.35 : w;
}

function scorePatternTiles(
  labels: Array<ColorCode | null>,
  garment: Uint8Array,
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
      const mode = tileMode(labels, garment, width, tx * tile, ty * tile, tile);
      tiles.push(mode);
      if (mode && mode !== "den" && mode !== "trang") colorful.add(mode);
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

function tileMode(
  labels: Array<ColorCode | null>,
  garment: Uint8Array,
  width: number,
  x0: number,
  y0: number,
  tile: number,
): ColorCode | null {
  const counts = new Map<ColorCode, number>();
  let n = 0;
  for (let y = y0; y < y0 + tile; y += 1) {
    for (let x = x0; x < x0 + tile; x += 1) {
      const i = y * width + x;
      if (!garment[i]) continue;
      const code = labels[i];
      if (!code) continue;
      counts.set(code, (counts.get(code) ?? 0) + 1);
      n += 1;
    }
  }
  if (!n) return null;
  let best: ColorCode | null = null;
  let bestN = 0;
  for (const [code, c] of counts) {
    if (c > bestN) {
      best = code;
      bestN = c;
    }
  }
  return best && bestN * 2 >= n ? best : null;
}

function promoteIfClose(
  share: Record<ColorCode, number>,
  keep: ColorCode,
  rivals: ColorCode[],
  ratio: number,
): void {
  const k = share[keep] ?? 0;
  if (k < 0.08) return;
  for (const r of rivals) {
    const v = share[r] ?? 0;
    if (v > 0 && k >= ratio * v) {
      share[keep] = k + v * 0.35;
      share[r] = v * 0.55;
    }
  }
}

function collapseGroup(share: Record<ColorCode, number>, group: ColorCode[]): void {
  let best: ColorCode | null = null;
  let bestV = 0;
  for (const code of group) {
    const v = share[code] ?? 0;
    if (v > bestV) {
      best = code;
      bestV = v;
    }
  }
  if (!best) return;
  for (const code of group) {
    if (code === best) continue;
    const v = share[code] ?? 0;
    // Keep a real second color (white embroidery, gingham white).
    if (v < 0.55 * bestV && v < 0.16) share[code] = 0;
  }
}

function hsl(
  r8: number,
  g8: number,
  b8: number,
): { h: number; s: number; l: number; chroma: number } {
  const r = r8 / 255;
  const g = g8 / 255;
  const b = b8 / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  const chroma = max - min;
  const den = 1 - Math.abs(2 * l - 1);
  const s = chroma <= 0 || den <= 0 ? 0 : Math.min(1, chroma / den);
  let h = 0;
  if (chroma > 0) {
    if (max === r) h = ((g - b) / chroma) % 6;
    else if (max === g) h = (b - r) / chroma + 2;
    else h = (r - g) / chroma + 4;
    h *= 60;
    if (h < 0) h += 360;
  }
  return { h, s, l, chroma };
}

function rgbDist(r: number, g: number, b: number, r2: number, g2: number, b2: number): number {
  const dr = r - r2;
  const dg = g - g2;
  const db = b - b2;
  return Math.sqrt(dr * dr + dg * dg + db * db);
}
