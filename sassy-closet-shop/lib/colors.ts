import { HUB_SLUG_HEX } from "@/lib/kit-catalog";
import type { ProductColor } from "@/lib/types";

export const COLOR_PRESETS: readonly { hex: string; name: string }[] = [
  { hex: "#F4F0E8", name: "Ivory" },
  { hex: "#111111", name: "Black" },
  { hex: "#FFFFFF", name: "White" },
  { hex: "#C4A484", name: "Tan" },
  { hex: "#5C4033", name: "Brown" },
  { hex: "#1C2A4A", name: "Navy" },
  { hex: "#6B6B6B", name: "Gray" },
  { hex: "#B08968", name: "Camel" },
  { hex: "#E8D5C4", name: "Blush" },
  { hex: "#7A8B6F", name: "Olive" },
  { hex: "#8B3A3A", name: "Wine" },
  { hex: "#D4C4B0", name: "Sand" },
];

export function normalizeHex(value: string): string | null {
  const trimmed = value.trim();
  const match = trimmed.match(/^#?([0-9a-f]{3}|[0-9a-f]{6})$/i);
  if (!match) {
    return null;
  }
  let digits = match[1] ?? "";
  if (digits.length === 3) {
    digits = `${digits[0]}${digits[0]}${digits[1]}${digits[1]}${digits[2]}${digits[2]}`;
  }
  return `#${digits.toUpperCase()}`;
}

export function createColorId(): string {
  const raw = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
  return `c${raw.replace(/[^a-z0-9]/gi, "").slice(0, 12).toLowerCase()}`;
}

const HUB_SLUGS = new Set(["kem", "xanh", "hoa", "do", "den", "hong", "cham-bi"]);

export function isColorId(value: string): boolean {
  const trimmed = value.trim();
  if (HUB_SLUGS.has(trimmed)) {
    return true;
  }
  return /^c[a-z0-9]{4,20}$/i.test(trimmed);
}

export function suggestedColorName(hex: string): string {
  const normalized = normalizeHex(hex);
  if (!normalized) {
    return "";
  }
  const preset = COLOR_PRESETS.find((item) => item.hex === normalized);
  return preset?.name ?? "";
}

/** True when the stored word is a real name — not empty, not `#F4F0E8`. */
export function isStoredColorWord(name: string): boolean {
  const trimmed = name.trim();
  if (!trimmed) {
    return false;
  }
  if (normalizeHex(trimmed)) {
    return false;
  }
  if (/^color\s*#/i.test(trimmed)) {
    return false;
  }
  return true;
}

/** Customer chip text. Admin name if stored; otherwise Color 1/2. Never invent Kem from hex. */
export function colorShopLabel(color: ProductColor, index: number): string {
  if (isStoredColorWord(color.name)) {
    return color.name.trim();
  }
  return `Color ${index + 1}`;
}

export function parseProductColor(raw: unknown, ma: string, index: number): ProductColor {
  if (typeof raw !== "object" || raw === null) {
    throw new Error(`Mã ${ma} color ${index} is invalid`);
  }
  const row = raw as Record<string, unknown>;
  const idRaw = row.id;
  const id =
    typeof idRaw === "string" && isColorId(idRaw) ? idRaw : `${createColorId()}${index}`;
  const hexFromRow = typeof row.hex === "string" ? normalizeHex(row.hex) : null;
  const hex = hexFromRow ?? HUB_SLUG_HEX[id] ?? null;
  if (!hex) {
    throw new Error(`Mã ${ma} color ${index} needs a hex value`);
  }
  const note = typeof row.note === "string" ? row.note.trim() : "";
  const nameRaw = typeof row.name === "string" ? row.name.trim() : "";
  const name = isStoredColorWord(nameRaw) ? nameRaw : "";
  return { id, hex, name, note };
}

export function colorById(
  colors: ProductColor[],
  colorId: string | null,
): ProductColor | undefined {
  if (!colorId) {
    return undefined;
  }
  return colors.find((color) => color.id === colorId);
}
