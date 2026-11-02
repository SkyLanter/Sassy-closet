import { hashBytes, saveSubmission } from "./store";
import { normalizeSourceLink } from "./source-link";
import { isPriceBreakdown } from "./pricing";
import { isTaobaoItem } from "./taobao";
import type { Piece } from "./types";

export async function saveFromForm(form: FormData, existingMa?: string) {
  const photos: { bytes: Buffer; hash: string; ext: string }[] = [];
  for (const value of form.getAll("photos")) {
    if (!(value instanceof File)) continue;
    const bytes = Buffer.from(await value.arrayBuffer());
    const ext = extFromName(value.name || "photo.jpg");
    photos.push({ bytes, hash: hashBytes(bytes), ext });
  }

  const pieces = piecesFromJson(String(form.get("pieces") ?? "").trim());
  const keep_photos = photoKeysFromJson(String(form.get("keep_photos") ?? "").trim());

  return saveSubmission({
    kind: String(form.get("kind") || form.get("prefix") || "A"),
    size: String(form.get("size") ?? ""),
    link: normalizeSourceLink(String(form.get("link") ?? "")),
    color: String(form.get("color") ?? ""),
    color_note: String(form.get("color_note") ?? ""),
    pieces,
    cost_usd: String(form.get("cost_usd") ?? ""),
    cost_cny: String(form.get("cost_cny") ?? ""),
    cost_currency: String(form.get("cost_currency") ?? "USD"),
    sell_usd: String(form.get("sell_usd") ?? ""),
    sell_cny: String(form.get("sell_cny") ?? ""),
    sell_currency: String(form.get("sell_currency") ?? "USD"),
    keep_photos,
    photos,
    existingMa,
    newMa: String(form.get("new_ma") ?? ""),
    needs_research: String(form.get("needs_research") ?? "") === "1",
    taobao_snapshot: parseJson(form.get("taobao_snapshot"), isTaobaoItem),
    auto_price: parseJson(form.get("auto_price"), isPriceBreakdown),
  });
}

function piecesFromJson(raw: string): Piece[] {
  const parsed = jsonValue(raw);
  if (!Array.isArray(parsed)) return [];
  const pieces: Piece[] = [];
  for (const item of parsed) {
    if (typeof item === "object" && item !== null && !Array.isArray(item)) pieces.push(item as Piece);
  }
  return pieces;
}

function photoKeysFromJson(raw: string): string[] {
  const parsed = jsonValue(raw);
  if (!Array.isArray(parsed)) return [];
  const keys: string[] = [];
  for (const item of parsed) {
    if (typeof item === "string") keys.push(item);
  }
  return keys;
}

function jsonValue(raw: string): unknown {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as unknown;
  } catch {
    return null;
  }
}

function parseJson<T>(raw: FormDataEntryValue | null, guard: (value: unknown) => value is T): T | null {
  const text = String(raw ?? "").trim();
  if (!text) return null;
  try {
    const parsed: unknown = JSON.parse(text);
    return guard(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

function extFromName(name: string): string {
  const ext = name.toLowerCase().match(/\.(jpe?g|png|webp)$/)?.[0];
  return ext ?? ".jpg";
}
