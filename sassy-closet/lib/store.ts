import { createHash } from "node:crypto";
import { isKindCode, kindLabel, sizeOptionsLine } from "./kinds";
import { notifyIntakeDatasetSyncWebhook } from "./intakeDatasetSyncWebhook";
import { formatMa, maExists, nextMa, normalizeMa, parseHubMa } from "./mint";
import { moneyForStore } from "./money-text";
import { mintBlock, publishBlock, wholeDollars } from "./publish-guard";
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
  if (!bag || typeof bag !== "object" || Array.isArray(bag)) return [];
  const raw = onHandBucket(bag, target, ma);
  return sanitizeOnHandRows(raw, target);
}

/** Exact canonical key wins. Otherwise one alias — never summed. A case-only spelling beats a padded one. */
function onHandBucket(bag: Record<string, unknown>, target: string, requested: string): unknown {
  if (bag[target] != null) return bag[target];
  if (requested !== target && bag[requested] != null) return bag[requested];
  if (!target) return undefined;
  const matches = Object.keys(bag).filter((key) => normalizeMa(key) === target && bag[key] != null);
  const caseOnly = matches.filter((key) => key.trim().toUpperCase() === target).sort();
  const pool = caseOnly.length > 0 ? caseOnly : [...matches].sort();
  const key = pool[0];
  return key === undefined ? undefined : bag[key];
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

/**
 * Slot number of `{ma}/001.jpg`.
 * A keep path can spell that same file with a leading slash, `./`, or `..`
 * that the photo store collapses, so those aliases occupy the slot too.
 * The folder matches through normalizeMa, so `a01` occupies the same slots as `A01`.
 */
function photoSlot(rel: string, ma: string): number | null {
  const parts = sanitizePhotoRel(rel)
    .split("/")
    .filter((part) => part.length > 0 && part !== ".");
  if (parts.length !== 2 || normalizeMa(parts[0] ?? "") !== normalizeMa(ma)) return null;
  const match = /^(\d+)\.[^.]+$/i.exec(parts[1] ?? "");
  if (!match) return null;
  const slot = Number(match[1]);
  if (!Number.isInteger(slot) || slot < 1 || slot > 9999) return null;
  return slot;
}

/**
 * Next `{ma}/NNN.ext` that is not already a kept photo.
 * Naming from keep_photos.length reuses 003 when 001 and 003 stay and 002 was
 * dropped, and that write replaces the kept file.
 */
function nextPhotoRel(ma: string, taken: ReadonlySet<number>, ext: string): { rel: string; slot: number } {
  let slot = 1;
  while (taken.has(slot)) {
    slot += 1;
    if (slot > 9999) {
      throw Object.assign(new Error("Quá nhiều ảnh cho mã này."), { status: 409 });
    }
  }
  return { rel: `${ma}/${String(slot).padStart(3, "0")}${ext}`, slot };
}

/**
 * `A01/001.jpg` for `/A01/001.jpg`, `A01/./001.jpg`, and `a01/001.jpg`.
 * The filename keeps its own case, so `001.JPG` does not share `001.jpg`.
 */
function photoHashKey(rel: string): string {
  const parsed = photoFolderAndRest(rel);
  if (!parsed) return "";
  return `${normalizeMa(parsed.folder)}/${parsed.rest}`;
}

/**
 * One hash per kept path, in keep order.
 * Equal-length path and hash lists pair by photoHashKey. The first stored
 * non-empty hash wins. A keep path with no pair stays "". Those lists are
 * not read from disk, so a path that was never stored stays empty.
 * Any other shape, including a missing hash list, is not lined up. Ignore
 * the stored hashes and hash the file the caller named, then the canonical
 * spelling when that path differs. A missing file stays "".
 */
async function keptPhotoHashes(
  existing: Submission | null,
  keep: readonly string[],
): Promise<string[]> {
  if (!existing) return keep.map(() => "");
  const paths = existing.photo_paths;
  const hashes = existing.photo_hashes;
  if (Array.isArray(paths) && Array.isArray(hashes) && paths.length === hashes.length) {
    const byKey = new Map<string, string>();
    for (let i = 0; i < paths.length; i += 1) {
      const rel = paths[i];
      const hash = hashes[i];
      if (typeof rel !== "string" || rel.length === 0) continue;
      if (typeof hash !== "string" || hash.length === 0) continue;
      const key = photoHashKey(rel);
      if (key.length === 0 || byKey.has(key)) continue;
      byKey.set(key, hash);
    }
    return keep.map((rel) => {
      if (typeof rel !== "string" || rel.length === 0) return "";
      const key = photoHashKey(rel);
      if (key.length === 0) return "";
      return byKey.get(key) ?? "";
    });
  }
  const backend = activeBackend();
  const out: string[] = [];
  for (const rel of keep) {
    out.push(await hashKeptFile(backend, rel));
  }
  return out;
}

async function hashKeptFile(backend: StoreBackend, rel: string): Promise<string> {
  if (typeof rel !== "string" || rel.length === 0) return "";
  const canonical = photoHashKey(rel);
  const sanitized = sanitizePhotoRel(rel);
  // The path the caller named, then the canonical spelling. A lowercase folder
  // and `A01/001.jpg` can both exist; the named file is the one being kept.
  const candidates: string[] = [];
  if (sanitized.length > 0) candidates.push(sanitized);
  if (canonical.length > 0 && canonical !== sanitized) candidates.push(canonical);
  for (const candidate of candidates) {
    const photo = await backend.readPhoto(candidate);
    if (photo) return hashBytes(photo.bytes);
  }
  return "";
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
  // The destination check above does not see the old code. Leaving a held
  // mã, or leaving S06 at a price the lock refuses, is the same save.
  if (existing && normalizeMa(existing.ma) !== normalizeMa(ma)) {
    const posted = postedSell(input.sell_currency, input.sell_usd, input.sell_cny);
    const sourceBlocked = publishBlock({
      action: "update",
      ma: existing.ma,
      sellUsd: posted,
      sellCurrency: input.sell_currency,
    });
    // A blank sell is not $25. Leaving S06 that way would drop the lock.
    const leavingLocked = normalizeMa(existing.ma) === "S06" && wholeDollars(posted) !== 25;
    if (sourceBlocked || leavingLocked) {
      const reason = sourceBlocked ?? "s06-lock";
      throw Object.assign(new Error(`Không lưu ${normalizeMa(existing.ma)} (${reason}).`), {
        status: 409,
      });
    }
  }

  const now = new Date().toISOString();
  const costCny = moneyForStore(input.cost_cny, "CNY");
  const costUsd = moneyForStore(input.cost_usd, "USD");
  const sellCny = moneyForStore(input.sell_cny, "CNY");
  const sellUsd = moneyForStore(input.sell_usd, "USD");
  const photoHashes = await keptPhotoHashes(existing, input.keep_photos);
  const oldMa = existing?.ma ?? "";
  const renaming = oldMa.length > 0 && normalizeMa(oldMa) !== normalizeMa(ma);
  const claimed = claimedPhotoPaths(store, existing?.id ?? null, input.keep_photos);
  const addedPhotos: { rel: string; photo: SaveInput["photos"][number] }[] = [];
  if (renaming) {
    // A renamed keep file keeps its old path when the new photo would use that
    // same length-based name. A save that stays on this mã still uses the first
    // free slot, so a gap does not overwrite a kept file. A path another row
    // still claims is not reused, so the new bytes do not replace that file.
    let index = input.keep_photos.length;
    for (const photo of input.photos) {
      let name = "";
      let rel = "";
      do {
        index += 1;
        if (index > 9999) {
          throw Object.assign(new Error("Quá nhiều ảnh cho mã này."), { status: 409 });
        }
        name = `${String(index).padStart(3, "0")}${photo.ext}`;
        rel = `${ma}/${name}`;
      } while (claimed.has(`${normalizeMa(ma)}/${name}`));
      addedPhotos.push({ rel, photo });
    }
  } else {
    const takenSlots = new Set<number>();
    for (const rel of input.keep_photos) {
      const slot = photoSlot(rel, ma);
      if (slot !== null) takenSlots.add(slot);
    }
    const canon = normalizeMa(ma);
    for (const photo of input.photos) {
      let next = nextPhotoRel(ma, takenSlots, photo.ext);
      while (claimed.has(`${canon}/${String(next.slot).padStart(3, "0")}${photo.ext}`)) {
        takenSlots.add(next.slot);
        next = nextPhotoRel(ma, takenSlots, photo.ext);
      }
      takenSlots.add(next.slot);
      addedPhotos.push({ rel: next.rel, photo });
    }
  }
  const reserved = new Set(addedPhotos.map((item) => item.rel));
  const photoPaths = await relocateKeptPhotos(oldMa, ma, input.keep_photos, reserved, claimed);

  const backend = activeBackend();
  for (const item of addedPhotos) {
    const parsed = photoFolderAndRest(item.rel);
    const claimKey = parsed ? `${normalizeMa(parsed.folder)}/${parsed.rest}` : "";
    if (claimKey.length > 0 && claimed.has(claimKey)) {
      throw Object.assign(new Error("Ảnh này đang thuộc mã khác."), { status: 409 });
    }
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
    price: sellUsd,
    cost_cny: costCny,
    cost_usd: costUsd,
    cost_currency: (input.cost_currency || "USD").toUpperCase(),
    sell_cny: sellCny,
    sell_usd: sellUsd,
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
  if (!hash) return [];
  return (await loadStore()).submissions.filter(
    (row) => Array.isArray(row.photo_hashes) && row.photo_hashes.includes(hash),
  );
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
      colorPieces(row.pieces),
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

/** Spreadsheet formula starters. A leading apostrophe keeps the cell as text. */
const CSV_FORMULA_START = /^[=+\-@\t\r]/;

function csvCell(value: string): string {
  const text = CSV_FORMULA_START.test(value) ? `'${value}` : value;
  if (text !== value || /[",\n\r]/.test(text)) return `"${text.replaceAll('"', '""')}"`;
  return text;
}

function colorPieces(pieces: unknown): string {
  if (!Array.isArray(pieces)) return "";
  const parts: string[] = [];
  for (let index = 0; index < pieces.length; index += 1) {
    const piece = pieces[index];
    if (piece === null || typeof piece !== "object" || Array.isArray(piece)) continue;
    const part = piecePart(piece, index);
    if (!part.endsWith(":")) parts.push(part);
  }
  return parts.join(" | ");
}

function piecePart(piece: object, index: number): string {
  const record = piece as { color?: unknown; suggested?: unknown };
  const color = typeof record.color === "string" ? record.color : "";
  const suggested = suggestedColor(record.suggested);
  return `P${index + 1}: ${color || suggested}`.trim();
}

function suggestedColor(suggested: unknown): string {
  if (!Array.isArray(suggested)) return "";
  const first = suggested[0];
  return typeof first === "string" ? first : "";
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
