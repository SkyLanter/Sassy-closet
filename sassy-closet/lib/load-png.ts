import { PNG } from "pngjs";
import { readFileSync } from "node:fs";

export function loadPngRgba(path: string): {
  data: Uint8Array;
  width: number;
  height: number;
} {
  const png = PNG.sync.read(readFileSync(path));
  return { data: png.data, width: png.width, height: png.height };
}

/** Match the live canvas downscale (max edge 192, nearest). */
export function downscaleNearest(
  src: Uint8Array,
  sw: number,
  sh: number,
  maxEdge = 192,
): { data: Uint8ClampedArray; width: number; height: number } {
  const scale = Math.min(1, maxEdge / Math.max(sw, sh));
  const w = Math.max(1, Math.round(sw * scale));
  const h = Math.max(1, Math.round(sh * scale));
  const data = new Uint8ClampedArray(w * h * 4);
  for (let y = 0; y < h; y += 1) {
    const sy = Math.min(sh - 1, Math.round((y + 0.5) / scale - 0.5));
    for (let x = 0; x < w; x += 1) {
      const sx = Math.min(sw - 1, Math.round((x + 0.5) / scale - 0.5));
      const si = (sy * sw + sx) * 4;
      const di = (y * w + x) * 4;
      data[di] = src[si];
      data[di + 1] = src[si + 1];
      data[di + 2] = src[si + 2];
      data[di + 3] = src[si + 3];
    }
  }
  return { data, width: w, height: h };
}
