import { createHash } from "node:crypto";
import { isKindCode } from "./kinds";
import { formatMa, maExists, nextMa, normalizeMa, parseHubMa } from "./mint";
import { sanitizeOnHandRows } from "./on-hand";
import { buildCaptionVi } from "./captions";
import {
  activeBackend,
  emptyStore,
  migrateLocalToDurableIfNeeded,
  photoContentType,
  sanitizePhotoRel,
  storageStatus,
} from "./store-backend";
import type { StoreFile } from "./store-backend";
import type { KindCode } from "./kinds";
import type { OnHandRow, Piece, Submission } from "./types";

export type { StoreFile, StorageMode } from "./store-backend";
export { storageMode, storageStatus, blobConfigured } from "./store-backend";

export type SaveInput = {
  kind: string;
  size: string;
  link: string;
  color: string;
  color_note: string;
  pieces: Piece[];
  cost_usd: string;
  cost_cny: string;
  cost_currency: string;
  sell_usd: string;
  sell_cny: string;
  sell_currency: string;
  keep_photos: string[];
  photos: { bytes: Buffer; hash: string; ext: string }[];
  existingMa?: string;
  newMa?: string;
};

async function loadStore(): Promise<StoreFile> {
  await migrateLocalToDurableIfNeeded();
  return (await activeBackend().readStore()) ?? emptyStore();
}

async function persistStore(store: StoreFile): Promise<void> {
  await activeBackend().writeStore(store);
}

export async function listSubmissions(): Promise<Submission[]> {
  return (await loadStore()).submissions;
}

export async function getSubmission(ma: string): Promise<Submission | null> {
  const target = normalizeMa(ma);
  return (await loadStore()).submissions.find((row) => normalizeMa(row.ma) === target) ?? null;
}

export async function getOnHandRows(ma: string): Promise<OnHandRow[]> {
  const target = normalizeMa(ma);
  const bag = (await loadStore()).on_hand;
  if (!bag || typeof bag !== "object") return [];
  const raw = bag[target] ?? bag[ma];
  return sanitizeOnHandRows(raw, target);
}

export async function listMas(): Promise<string[]> {
  return (await loadStore()).submissions.map((row) => row.ma);
}

export async function getFx(): Promise<{ usd_cny: number; updated: string; label: string }> {
  const fx = (await loadStore()).fx;
  return {
    ...fx,
    label: `Tỷ giá: 1 USD = ${fx.usd_cny} ¥ CNY · cập nhật mỗi tuần`,
  };
}

export async function setFx(
  usdCny: number,
): Promise<{ usd_cny: number; updated: string; label: string }> {
  const store = await loadStore();
  store.fx = {
    usd_cny: usdCny,
    updated: new Date().toISOString().slice(0, 10),
  };
  await persistStore(store);
  return getFx();
}

export async function saveSubmission(input: SaveInput): Promise<Submission> {
  if (!isKindCode(input.kind)) {
    throw Object.assign(new Error("Loại đồ không đúng."), { status: 400 });
  }
  const store = await loadStore();
  const mas = store.submissions.map((row) => row.ma);
  const existing = input.existingMa
    ? store.submissions.find((row) => normalizeMa(row.ma) === normalizeMa(input.existingMa!)) ??
      null
    : null;
  if (input.existingMa && !existing) {
    throw Object.assign(new Error("Không tìm thấy mã này 🥺"), { status: 404 });
  }

  const ma = resolveSaveMa({
    kind: input.kind,
    existing,
    newMa: input.newMa,
    mas,
  });

  const now = new Date().toISOString();
  const photoPaths = [...input.keep_photos];
  const photoHashes = existing ? [...existing.photo_hashes] : [];
  if (input.keep_photos.length === 0 && existing) {
    photoHashes.length = 0;
  }

  const backend = activeBackend();
  let index = photoPaths.length;
  for (const photo of input.photos) {
    index += 1;
    const name = `${String(index).padStart(3, "0")}${photo.ext}`;
    const rel = `${ma}/${name}`;
    await backend.writePhoto(rel, photo.bytes, photoContentType(rel));
    photoPaths.push(rel);
    photoHashes.push(photo.hash);
  }

  const base: Submission = {
    id: existing?.id ?? store.nextId,
    ma,
    kind: input.kind,
    size: input.size.trim(),
    color: input.color.trim(),
    color_note: input.color_note.trim(),
    pieces: input.pieces,
    link: input.link.trim(),
    price: input.sell_usd.trim(),
    cost_cny: input.cost_cny.trim(),
    cost_usd: input.cost_usd.trim(),
    cost_currency: (input.cost_currency || "USD").toUpperCase(),
    sell_cny: input.sell_cny.trim(),
    sell_usd: input.sell_usd.trim(),
    sell_currency: (input.sell_currency || "USD").toUpperCase(),
    blurb: "",
    photo_paths: photoPaths,
    photo_hashes: photoHashes,
    status: "staged",
    square: "not_square",
    created_at: existing?.created_at ?? now,
    updated_at: now,
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: `Documents/Sassy Closet/Photos/${ma}/`,
  };
  base.caption_vi = buildCaptionVi(base);

  if (existing) {
    store.submissions = store.submissions.map((row) => (row.id === existing.id ? base : row));
  } else {
    store.nextId += 1;
    store.submissions.push(base);
  }
  await persistStore(store);
  return base;
}

export async function findByPhotoHash(hash: string): Promise<Submission[]> {
  return (await loadStore()).submissions.filter((row) => row.photo_hashes.includes(hash));
}

export async function readPhoto(rel: string): Promise<{ bytes: Buffer; type: string } | null> {
  await migrateLocalToDurableIfNeeded();
  const safe = sanitizePhotoRel(rel);
  return activeBackend().readPhoto(safe);
}

export function hashBytes(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

export async function exportCsv(): Promise<string> {
  const headers = [
    "ma",
    "kind",
    "kind_vi",
    "size",
    "color",
    "color_note",
    "color_pieces",
    "blurb",
    "cost_cny",
    "cost_usd",
    "cost_currency",
    "sell_cny",
    "sell_usd",
    "sell_currency",
    "source_link",
    "status",
    "square",
    "created_at",
    "updated_at",
    "photo_link",
  ];
  const rows = (await loadStore()).submissions.map((row) =>
    [
      row.ma,
      row.kind,
      kindVi(row.kind),
      row.size,
      row.color,
      row.color_note,
      row.pieces
        .map((piece, i) => `P${i + 1}: ${piece.color || piece.suggested[0] || ""}`.trim())
        .filter((part) => !part.endsWith(":"))
        .join(" | "),
      row.blurb,
      row.cost_cny,
      row.cost_usd,
      row.cost_currency,
      row.sell_cny,
      row.sell_usd,
      row.sell_currency,
      row.link,
      row.status,
      row.square,
      row.created_at,
      row.updated_at,
      row.photo_link,
    ]
      .map(csvCell)
      .join(","),
  );
  return [headers.join(","), ...rows].join("\n") + "\n";
}

export function storeHealth(): ReturnType<typeof storageStatus> {
  return storageStatus();
}

function kindVi(kind: KindCode): string {
  switch (kind) {
    case "A":
      return "Áo";
    case "Q":
      return "Quần";
    case "V":
      return "Váy";
    case "K":
      return "Áo khoác";
    case "G":
      return "Giày";
    case "B":
      return "Túi";
    case "P":
      return "Phụ kiện";
    case "H":
      return "Tóc";
    case "J":
      return "Trang sức";
    case "S":
      return "Set đồ";
    case "O":
      return "Khác / Other";
    default: {
      const _never: never = kind;
      return _never;
    }
  }
}

function csvCell(value: string): string {
  if (/[",\n]/.test(value)) return `"${value.replaceAll('"', '""')}"`;
  return value;
}

function resolveSaveMa(input: {
  kind: KindCode;
  existing: Submission | null;
  newMa?: string;
  mas: string[];
}): string {
  const raw = (input.newMa ?? "").trim();
  if (!raw) {
    if (input.existing) return input.existing.ma;
    return nextMa(input.kind, input.mas);
  }
  const parsed = parseHubMa(raw);
  if (parsed) {
    const formatted = formatMa(parsed.kind, parsed.n);
    if (input.existing && formatted === input.existing.ma) return formatted;
    if (maExists(input.mas, formatted, input.existing?.ma)) {
      throw Object.assign(new Error(`Mã ${formatted} đã có rồi — không gộp nha 💕`), {
        status: 409,
      });
    }
    return formatted;
  }
  if (isKindCode(raw.toUpperCase())) {
    const minted = nextMa(raw.toUpperCase() as KindCode, input.mas);
    if (input.existing && minted === input.existing.ma) return minted;
    return minted;
  }
  throw Object.assign(
    new Error("Mã mới: chữ P (ra P kế) hoặc đủ số kiểu P10 nha 💕"),
    { status: 400 },
  );
}
