import { createHash } from "node:crypto";
import { isKindCode, kindLabel, sizeOptionsLine } from "./kinds";
import { notifyIntakeDatasetSyncWebhook } from "./intakeDatasetSyncWebhook";
import { formatMa, maExists, nextMa, normalizeMa, parseHubMa } from "./mint";
import { mintBlock, publishBlock } from "./publish-guard";
import { normalizeSourceLink } from "./source-link";
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
import type { StoreBackend, StoreFile } from "./store-backend";
import type { KindCode } from "./kinds";
import type { OnHandRow, Piece, Submission } from "./types";
import type { PriceBreakdown } from "./pricing";
import type { TaobaoItem } from "./taobao";

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
  needs_research: boolean;
  taobao_snapshot: TaobaoItem | null;
  auto_price: PriceBreakdown | null;
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
  const blocked = publishBlock({
    action: existing ? "update" : "create",
    ma,
    sellUsd: postedSell(input.sell_currency, input.sell_usd, input.sell_cny),
    sellCurrency: input.sell_currency,
  });
  if (blocked) {
    throw Object.assign(new Error(`Không lưu ${ma} (${blocked}).`), { status: 409 });
  }

  const now = new Date().toISOString();
  const photoHashes = existing ? [...existing.photo_hashes] : [];
  if (input.keep_photos.length === 0 && existing) {
    photoHashes.length = 0;
  }

  // Length-based names stay as they are. Reserve them so a renamed keep file
  // with that same name is left on the old path instead of being replaced.
  const addedPhotos: { rel: string; photo: SaveInput["photos"][number] }[] = [];
  let index = input.keep_photos.length;
  for (const photo of input.photos) {
    index += 1;
    const name = `${String(index).padStart(3, "0")}${photo.ext}`;
    addedPhotos.push({ rel: `${ma}/${name}`, photo });
  }
  const reserved = new Set(addedPhotos.map((item) => item.rel));
  const claimed = claimedPhotoPaths(store, existing?.id ?? null, input.keep_photos);
  const photoPaths = await relocateKeptPhotos(
    existing?.ma ?? "",
    ma,
    input.keep_photos,
    reserved,
    claimed,
  );

  const backend = activeBackend();
  for (const item of addedPhotos) {
    await backend.writePhoto(item.rel, item.photo.bytes, photoContentType(item.rel));
    photoPaths.push(item.rel);
    photoHashes.push(item.photo.hash);
  }

  const base: Submission = {
    id: existing?.id ?? store.nextId,
    ma,
    kind: input.kind,
    size: input.size.trim(),
    color: input.color.trim(),
    color_note: input.color_note.trim(),
    pieces: input.pieces,
    link: normalizeSourceLink(input.link),
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
    needs_research: input.needs_research,
    taobao_snapshot: input.taobao_snapshot,
    auto_price: input.auto_price,
    created_at: existing?.created_at ?? now,
    updated_at: now,
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: `Documents/Sassy Closet/Photos/${ma}/`,
  };
  base.caption_vi = buildCaptionVi(base, store.fx.usd_cny);

  if (existing) {
    store.submissions = store.submissions.map((row) => (row.id === existing.id ? base : row));
  } else {
    store.nextId += 1;
    store.submissions.push(base);
  }
  await persistStore(store);
  await notifyIntakeDatasetSyncWebhook(existing ? "update" : "create", base, existing);
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
    "size_options",
  ];
  const rows = (await loadStore()).submissions.map((row) =>
    [
      row.ma,
      row.kind,
      kindLabel(row.kind),
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
      sizeOptionsLine(row.kind),
    ]
      .map(csvCell)
      .join(","),
  );
  return [headers.join(","), ...rows].join("\n") + "\n";
}

export function storeHealth(): ReturnType<typeof storageStatus> {
  return storageStatus();
}

function csvCell(value: string): string {
  if (/[",\n]/.test(value)) return `"${value.replaceAll('"', '""')}"`;
  return value;
}

/**
 * Staff rename updates `ma` and `photo_link` but the kept files still live at
 * `{old}/NNN.ext`. Copy those bytes under the new mã and store the new path.
 * The old file stays. Skip a destination that a new photo will write, that
 * another row or keep path already claims, or that already holds different
 * bytes, so this copy cannot replace a live file.
 */
async function relocateKeptPhotos(
  oldMa: string,
  newMa: string,
  keep: readonly string[],
  reserved: ReadonlySet<string>,
  claimed: ReadonlySet<string>,
): Promise<string[]> {
  if (!oldMa || oldMa === newMa) return [...keep];
  const oldCanon = normalizeMa(oldMa);
  if (!oldCanon) return [...keep];
  const backend = activeBackend();
  const next: string[] = [];
  const placed = new Set<string>();
  for (const rel of keep) {
    const parsed = photoFolderAndRest(rel);
    if (!parsed || normalizeMa(parsed.folder) !== oldCanon) {
      next.push(rel);
      continue;
    }
    const dest = `${newMa}/${parsed.rest}`;
    const ownKey = `${normalizeMa(parsed.folder)}/${parsed.rest}`;
    const destKey = `${normalizeMa(newMa)}/${parsed.rest}`;
    if (dest === rel || dest === sanitizePhotoRel(rel)) {
      next.push(rel);
      continue;
    }
    // A reserved name is about to be written by the new photo. A claimed name
    // belongs to another row or to a keep path that is staying put.
    if (reserved.has(dest) || (claimed.has(destKey) && destKey !== ownKey)) {
      next.push(rel);
      continue;
    }
    if (placed.has(dest)) {
      next.push((await sameBytesAt(backend, dest, rel)) ? dest : rel);
      continue;
    }
    const photo = await backend.readPhoto(rel);
    if (!photo) {
      next.push(rel);
      continue;
    }
    const occupied = await backend.readPhoto(dest);
    if (occupied && !occupied.bytes.equals(photo.bytes)) {
      next.push(rel);
      continue;
    }
    if (!occupied) {
      await backend.writePhoto(dest, photo.bytes, photo.type || photoContentType(dest));
    }
    placed.add(dest);
    next.push(dest);
  }
  return next;
}

async function sameBytesAt(backend: StoreBackend, dest: string, rel: string): Promise<boolean> {
  const [left, right] = await Promise.all([backend.readPhoto(dest), backend.readPhoto(rel)]);
  return Boolean(left && right && left.bytes.equals(right.bytes));
}

function claimedPhotoPaths(
  store: StoreFile,
  exceptId: number | null,
  keep: readonly string[],
): Set<string> {
  const claimed = new Set<string>();
  for (const row of store.submissions) {
    if (exceptId !== null && row.id === exceptId) continue;
    if (!Array.isArray(row.photo_paths)) continue;
    for (const rel of row.photo_paths) addPhotoClaim(claimed, rel);
  }
  for (const rel of keep) addPhotoClaim(claimed, rel);
  return claimed;
}

function addPhotoClaim(target: Set<string>, rel: string): void {
  const parsed = photoFolderAndRest(rel);
  if (!parsed) return;
  target.add(`${normalizeMa(parsed.folder)}/${parsed.rest}`);
}

function photoFolderAndRest(rel: string): { folder: string; rest: string } | null {
  if (typeof rel !== "string" || rel.length === 0) return null;
  const parts = sanitizePhotoRel(rel)
    .split("/")
    .filter((part) => part.length > 0 && part !== ".");
  if (parts.length < 2) return null;
  const folder = parts[0] ?? "";
  const rest = parts.slice(1).join("/");
  if (!folder || !rest) return null;
  return { folder, rest };
}

function postedSell(currency: string, usd: string, cny: string): string {
  const cur = currency.trim().toUpperCase();
  const usdTrim = usd.trim();
  const cnyTrim = cny.trim();
  if (cur === "CNY" && cnyTrim) return cnyTrim;
  if (cur === "USD" && usdTrim) return usdTrim;
  return usdTrim || cnyTrim;
}

function guardedMint(kind: KindCode, mas: string[]): string {
  const blocked = mintBlock(kind, mas);
  if (blocked) {
    const ma = nextMa(kind, mas);
    throw Object.assign(new Error(`Không mint ${ma} (${blocked}).`), { status: 409 });
  }
  return nextMa(kind, mas);
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
    return guardedMint(input.kind, input.mas);
  }
  const parsed = parseHubMa(raw);
  if (parsed) {
    const formatted = formatMa(parsed.kind, parsed.n);
    const blocked = publishBlock({ action: input.existing ? "update" : "create", ma: formatted });
    if (blocked) {
      throw Object.assign(new Error(`Không lưu ${formatted} (${blocked}).`), { status: 409 });
    }
    if (input.existing && formatted === input.existing.ma) return formatted;
    if (maExists(input.mas, formatted, input.existing?.ma)) {
      throw Object.assign(new Error(`Mã ${formatted} đã có rồi — không gộp nha 💕`), {
        status: 409,
      });
    }
    return formatted;
  }
  if (isKindCode(raw.toUpperCase())) {
    return guardedMint(raw.toUpperCase() as KindCode, input.mas);
  }
  throw Object.assign(
    new Error("Mã mới: chữ P (ra P kế) hoặc đủ số kiểu P10 nha 💕"),
    { status: 400 },
  );
}
