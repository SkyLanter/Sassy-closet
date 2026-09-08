import fs from "node:fs";
import path from "node:path";
import { get, put } from "@vercel/blob";
import { dataRoot, ensureDataDirs } from "./paths";
import type { Submission } from "./types";

export type StoreFile = {
  nextId: number;
  submissions: Submission[];
  fx: { usd_cny: number; updated: string };
  on_hand?: Record<string, unknown>;
};

export type PhotoBytes = {
  bytes: Buffer;
  type: string;
};

export type StorageMode = "durable" | "local" | "ephemeral";

export type StoreBackend = {
  kind: "disk" | "blob";
  readStore(): Promise<StoreFile | null>;
  writeStore(store: StoreFile): Promise<void>;
  readPhoto(rel: string): Promise<PhotoBytes | null>;
  writePhoto(rel: string, bytes: Buffer, type: string): Promise<void>;
};

export const STORE_BLOB_PATH = "sassy-closet/store.json";
export const PHOTO_BLOB_PREFIX = "sassy-closet/photos/";

export function emptyStore(): StoreFile {
  return {
    nextId: 1,
    submissions: [],
    fx: { usd_cny: 6.71, updated: "2026-09-07" },
  };
}

export function blobConfigured(): boolean {
  return Boolean(
    process.env.BLOB_READ_WRITE_TOKEN?.trim() || process.env.BLOB_STORE_ID?.trim(),
  );
}

export function storageMode(): StorageMode {
  if (blobConfigured()) return "durable";
  if (process.env.VERCEL) return "ephemeral";
  return "local";
}

export function storageStatus(): {
  mode: StorageMode;
  durable: boolean;
  warning?: string;
} {
  const mode = storageMode();
  if (mode === "durable") return { mode, durable: true };
  if (mode === "ephemeral") {
    return {
      mode,
      durable: false,
      warning:
        "Vercel /tmp — redeploy xóa mã và ảnh. Gắn Private Blob store (xem sassy-closet/README.md).",
    };
  }
  return { mode, durable: false };
}

export function blobAccess(): "private" | "public" {
  const raw = (process.env.BLOB_ACCESS ?? "private").trim().toLowerCase();
  return raw === "public" ? "public" : "private";
}

export function photoContentType(rel: string): string {
  const ext = path.extname(rel).toLowerCase();
  if (ext === ".png") return "image/png";
  if (ext === ".webp") return "image/webp";
  return "image/jpeg";
}

export function sanitizePhotoRel(rel: string): string {
  return rel.replace(/^\/+/, "").replace(/\.\./g, "");
}

export function createLocalBackend(root: string): StoreBackend {
  const storeFile = (): string => path.join(root, "submissions.json");
  const photosRoot = (): string => path.resolve(root, "photos");

  return {
    kind: "disk",
    async readStore() {
      const file = storeFile();
      if (!fs.existsSync(file)) return null;
      return parseStore(fs.readFileSync(file, "utf8"));
    },
    async writeStore(store) {
      fs.mkdirSync(photosRoot(), { recursive: true });
      fs.writeFileSync(storeFile(), JSON.stringify(store, null, 2));
    },
    async readPhoto(rel) {
      const file = resolveLocalPhoto(photosRoot(), rel);
      if (!file || !fs.existsSync(file)) return null;
      return { bytes: fs.readFileSync(file), type: photoContentType(rel) };
    },
    async writePhoto(rel, bytes) {
      const file = resolveLocalPhoto(photosRoot(), rel);
      if (!file) {
        throw Object.assign(new Error("Đường dẫn ảnh không hợp lệ."), { status: 400 });
      }
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, bytes);
    },
  };
}

export function createBlobBackend(): StoreBackend {
  const access = blobAccess();
  return {
    kind: "blob",
    async readStore() {
      const result = await get(STORE_BLOB_PATH, { access, useCache: false });
      if (!result || result.statusCode !== 200 || !result.stream) return null;
      const raw = (await streamToBuffer(result.stream)).toString("utf8");
      if (!raw.trim()) return null;
      return parseStore(raw);
    },
    async writeStore(store) {
      await put(STORE_BLOB_PATH, JSON.stringify(store, null, 2), {
        access,
        addRandomSuffix: false,
        allowOverwrite: true,
        contentType: "application/json",
        cacheControlMaxAge: 0,
      });
    },
    async readPhoto(rel) {
      const safe = sanitizePhotoRel(rel);
      const result = await get(`${PHOTO_BLOB_PREFIX}${safe}`, { access, useCache: true });
      if (!result || result.statusCode !== 200 || !result.stream) return null;
      return {
        bytes: await streamToBuffer(result.stream),
        type: result.blob.contentType || photoContentType(safe),
      };
    },
    async writePhoto(rel, bytes, type) {
      const safe = sanitizePhotoRel(rel);
      await put(`${PHOTO_BLOB_PREFIX}${safe}`, bytes, {
        access,
        addRandomSuffix: false,
        allowOverwrite: true,
        contentType: type,
      });
    },
  };
}

export function activeBackend(): StoreBackend {
  if (blobConfigured()) return createBlobBackend();
  return createLocalBackend(ensureDataDirs());
}

export async function copyStoreAndPhotos(
  from: StoreBackend,
  to: StoreBackend,
): Promise<{ submissions: number; photos: number }> {
  const store = await from.readStore();
  if (!store || store.submissions.length === 0) {
    return { submissions: 0, photos: 0 };
  }
  let photos = 0;
  for (const row of store.submissions) {
    for (const rel of row.photo_paths ?? []) {
      const photo = await from.readPhoto(rel);
      if (!photo) continue;
      await to.writePhoto(rel, photo.bytes, photo.type);
      photos += 1;
    }
  }
  await to.writeStore(store);
  return { submissions: store.submissions.length, photos };
}

let migrateOnce: Promise<boolean> | null = null;

export function resetStoreBackendForTests(): void {
  migrateOnce = null;
}

export async function migrateLocalToDurableIfNeeded(): Promise<boolean> {
  if (!blobConfigured()) return false;
  if (!migrateOnce) {
    migrateOnce = runLegacyLocalMigrate();
  }
  return migrateOnce;
}

export function legacyLocalRoots(): string[] {
  const roots = new Set<string>();
  if (process.env.SASSY_DATA_DIR?.trim()) roots.add(process.env.SASSY_DATA_DIR.trim());
  roots.add(path.join(process.cwd(), "data"));
  roots.add(path.join("/tmp", "sassy-closet-data"));
  roots.add(dataRoot());
  return [...roots];
}

async function runLegacyLocalMigrate(): Promise<boolean> {
  const dest = createBlobBackend();
  const existing = await dest.readStore();
  if (existing && existing.submissions.length > 0) return false;
  for (const root of legacyLocalRoots()) {
    if (!fs.existsSync(path.join(root, "submissions.json"))) continue;
    const copied = await copyStoreAndPhotos(createLocalBackend(root), dest);
    if (copied.submissions > 0) return true;
  }
  return false;
}

export function parseStore(raw: string): StoreFile {
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw Object.assign(new Error("Kho mã đọc lỗi — không ghi đè."), { status: 500 });
  }
  if (!parsed || typeof parsed !== "object" || !Array.isArray((parsed as StoreFile).submissions)) {
    throw Object.assign(new Error("Kho mã không đúng dạng — không ghi đè."), { status: 500 });
  }
  const rec = parsed as StoreFile;
  return {
    nextId: typeof rec.nextId === "number" ? rec.nextId : 1,
    submissions: rec.submissions,
    fx: rec.fx ?? { usd_cny: 6.71, updated: "2026-09-07" },
    on_hand: rec.on_hand,
  };
}

function resolveLocalPhoto(photosRoot: string, rel: string): string | null {
  const safe = sanitizePhotoRel(rel);
  const file = path.resolve(photosRoot, safe);
  const root = photosRoot.endsWith(path.sep) ? photosRoot : photosRoot + path.sep;
  if (file !== photosRoot && !file.startsWith(root)) return null;
  return file;
}

async function streamToBuffer(stream: ReadableStream<Uint8Array>): Promise<Buffer> {
  return Buffer.from(await new Response(stream).arrayBuffer());
}
