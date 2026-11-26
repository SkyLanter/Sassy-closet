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

  const pieces = parsePiecesField(form.get("pieces"));
  const keep_photos = parseKeepPhotosField(form.get("keep_photos"));

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

function parsePiecesField(raw: FormDataEntryValue | null): Piece[] {
  const text = String(raw ?? "").trim();
  if (!text) return [];
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    return [];
  }
  if (!Array.isArray(parsed)) {
    throw Object.assign(new Error("Danh sách màu không đúng định dạng."), { status: 400 });
  }
  return parsed.filter(isPiece);
}

function parseKeepPhotosField(raw: FormDataEntryValue | null): string[] {
  const text = String(raw ?? "").trim();
  if (!text) return [];
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    return [];
  }
  if (!Array.isArray(parsed)) {
    throw Object.assign(new Error("Dữ liệu ảnh giữ không đúng định dạng."), { status: 400 });
  }
  return parsed.filter((item): item is string => typeof item === "string");
}

function isPiece(value: unknown): value is Piece {
  if (!value || typeof value !== "object") return false;
  const piece = value as Piece;
  return (
    typeof piece.id === "string" &&
    Array.isArray(piece.photos) &&
    Array.isArray(piece.suggested) &&
    typeof piece.color === "string" &&
    typeof piece.note === "string"
  );
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
