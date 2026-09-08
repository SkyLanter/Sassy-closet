import { hashBytes, saveSubmission } from "./store";
import { normalizeSourceLink } from "./source-link";
import type { Piece } from "./types";

export async function saveFromForm(form: FormData, existingMa?: string) {
  const photos: { bytes: Buffer; hash: string; ext: string }[] = [];
  for (const value of form.getAll("photos")) {
    if (!(value instanceof File)) continue;
    const bytes = Buffer.from(await value.arrayBuffer());
    const ext = extFromName(value.name || "photo.jpg");
    photos.push({ bytes, hash: hashBytes(bytes), ext });
  }

  let pieces: Piece[] = [];
  const rawPieces = String(form.get("pieces") ?? "").trim();
  if (rawPieces) {
    try {
      pieces = JSON.parse(rawPieces) as Piece[];
    } catch {
      pieces = [];
    }
  }

  let keep_photos: string[] = [];
  const rawKeep = String(form.get("keep_photos") ?? "").trim();
  if (rawKeep) {
    try {
      keep_photos = JSON.parse(rawKeep) as string[];
    } catch {
      keep_photos = [];
    }
  }

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
  });
}

function extFromName(name: string): string {
  const ext = name.toLowerCase().match(/\.(jpe?g|png|webp)$/)?.[0];
  return ext ?? ".jpg";
}
