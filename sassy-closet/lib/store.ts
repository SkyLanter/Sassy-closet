import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { isKindCode } from "./kinds";
import { formatMa, maExists, nextMa, normalizeMa, parseHubMa } from "./mint";
import { sanitizeOnHandRows } from "./on-hand";
import { buildCaptionVi } from "./captions";
import { photosRoot, submissionsFile } from "./paths";
import type { KindCode } from "./kinds";
import type { OnHandRow, Piece, Submission } from "./types";

type StoreFile = {
  nextId: number;
  submissions: Submission[];
  fx: { usd_cny: number; updated: string };
  on_hand?: Record<string, unknown>;
};

const globalStore = globalThis as typeof globalThis & {
  __sassyStore?: StoreFile;
};

function storePath(): string {
  return submissionsFile();
}

export function clearStoreCache(): void {
  delete globalStore.__sassyStore;
}

function emptyStore(): StoreFile {
  return {
    nextId: 1,
    submissions: [],
    fx: { usd_cny: 6.71, updated: "2026-09-07" },
  };
}

function readStore(): StoreFile {
  if (globalStore.__sassyStore) return globalStore.__sassyStore;
  const file = storePath();
  if (!fs.existsSync(file)) {
    const created = emptyStore();
    globalStore.__sassyStore = created;
    return created;
  }
  const parsed = JSON.parse(fs.readFileSync(file, "utf8")) as StoreFile;
  globalStore.__sassyStore = parsed;
  return parsed;
}

function writeStore(store: StoreFile): void {
  globalStore.__sassyStore = store;
  fs.writeFileSync(storePath(), JSON.stringify(store, null, 2));
}

export function listSubmissions(): Submission[] {
  return readStore().submissions;
}

export function getSubmission(ma: string): Submission | null {
  const target = normalizeMa(ma);
  return readStore().submissions.find((row) => normalizeMa(row.ma) === target) ?? null;
}

export function getOnHandRows(ma: string): OnHandRow[] {
  const target = normalizeMa(ma);
  const bag = readStore().on_hand;
  if (!bag || typeof bag !== "object") return [];
  const raw = bag[target] ?? bag[ma];
  return sanitizeOnHandRows(raw, target);
}

export function listMas(): string[] {
  return readStore().submissions.map((row) => row.ma);
}

export function getFx(): { usd_cny: number; updated: string; label: string } {
  const fx = readStore().fx;
  return {
    ...fx,
    label: `Tỷ giá: 1 USD = ${fx.usd_cny} ¥ CNY · cập nhật mỗi tuần`,
  };
}

export function setFx(usdCny: number): { usd_cny: number; updated: string; label: string } {
  const store = readStore();
  store.fx = {
    usd_cny: usdCny,
    updated: new Date().toISOString().slice(0, 10),
  };
  writeStore(store);
  return getFx();
}

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

export function saveSubmission(input: SaveInput): Submission {
  if (!isKindCode(input.kind)) {
    throw Object.assign(new Error("Loại đồ không đúng."), { status: 400 });
  }
  const store = readStore();
  const mas = store.submissions.map((row) => row.ma);
  const existing = input.existingMa ? getSubmission(input.existingMa) : null;
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
  let photoPaths = [...input.keep_photos];
  const photoHashes = existing ? [...existing.photo_hashes] : [];
  if (input.keep_photos.length === 0 && existing) {
    photoHashes.length = 0;
  } else if (existing && existing.ma !== ma) {
    photoPaths = relocateKeptPhotos(photoPaths, existing.ma, ma);
  }

  const photoDir = path.join(photosRoot(), ma);
  fs.mkdirSync(photoDir, { recursive: true });
  let index = photoPaths.length;
  for (const photo of input.photos) {
    index += 1;
    const name = `${String(index).padStart(3, "0")}${photo.ext}`;
    const rel = `${ma}/${name}`;
    fs.writeFileSync(path.join(photosRoot(), rel), photo.bytes);
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
    store.submissions = store.submissions.map((row) =>
      row.id === existing.id ? base : row,
    );
  } else {
    store.nextId += 1;
    store.submissions.push(base);
  }
  writeStore(store);
  return base;
}

export function findByPhotoHash(hash: string): Submission[] {
  return readStore().submissions.filter((row) => row.photo_hashes.includes(hash));
}

export function readPhoto(rel: string): { bytes: Buffer; type: string } | null {
  const safe = safePhotoRel(rel);
  if (!safe) return null;
  const root = photosRoot();
  const file = path.join(root, safe);
  if (!file.startsWith(root)) return null;
  if (!fs.existsSync(file)) return null;
  const ext = path.extname(file).toLowerCase();
  const type =
    ext === ".png" ? "image/png" : ext === ".webp" ? "image/webp" : "image/jpeg";
  return { bytes: fs.readFileSync(file), type };
}

export function hashBytes(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

export function exportCsv(): string {
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
  const rows = readStore().submissions.map((row) =>
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

function safePhotoRel(rel: string): string | null {
  const cleaned = rel.replace(/^\/+/, "").replace(/\.\./g, "");
  if (!cleaned || cleaned.includes("\0")) return null;
  return cleaned;
}

function relocateKeptPhotos(keep: string[], fromMa: string, toMa: string): string[] {
  if (fromMa === toMa) return keep;
  const root = photosRoot();
  const next: string[] = [];
  const copied: string[] = [];
  for (const rel of keep) {
    const safe = safePhotoRel(rel);
    if (!safe) continue;
    const name = path.basename(safe);
    const destRel = `${toMa}/${name}`;
    const src = path.join(root, safe);
    const dest = path.join(root, destRel);
    if (!src.startsWith(root) || !dest.startsWith(root)) continue;
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    if (fs.existsSync(src) && path.resolve(src) !== path.resolve(dest)) {
      fs.copyFileSync(src, dest);
      copied.push(src);
    }
    next.push(destRel);
  }
  for (const src of copied) {
    if (fs.existsSync(src)) fs.unlinkSync(src);
  }
  const oldDir = path.join(root, fromMa);
  if (oldDir.startsWith(root) && fs.existsSync(oldDir)) {
    try {
      fs.rmdirSync(oldDir);
    } catch {
      // leftover files stay; do not wipe another mã's folder
    }
  }
  return next;
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
