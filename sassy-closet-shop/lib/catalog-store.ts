import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { get, list, put } from "@vercel/blob";
import { createClient } from "@vercel/kv";
import seedCatalog from "@/data/products.json";
import {
  getCatalogBlobPath,
  readCatalogFromBlobPort,
  readJsonFromBlobPort,
  writeCatalogToBlobPort,
  type BlobCatalogPort,
} from "@/lib/blob-catalog";
import { assertLiveCatalogIntegrity, CatalogCorruptError, isCatalogCorruptError } from "@/lib/catalog-integrity";
import { applyHubColorNames } from "@/lib/hub-import";
import { applyRecordedHubSourceLink } from "@/lib/hub-source-links";
import { catalogShaOf, isInPlaceCoverPath } from "@/lib/catalog-sha";
import { srcBelongsToMa } from "@/lib/product-media";
import { catalogBlobPath, catalogBlobPrefix, catalogImagePrefix, catalogKvKey, isKnownSeedMa } from "@/lib/catalog-contract";
import { TYPE_LABELS } from "@/lib/catalog";
import { customerOpsVoiceHit } from "@/lib/public-safety";
import {
  BLOB_READBACK_DELAYS_MS,
  catalogFieldDiffs,
  waitMs,
} from "@/lib/catalog-roundtrip";
import {
  assertCanonicalSerializedCatalog,
  parseCatalogDocument,
  stampCatalogUpdatedAt,
  toCatalogDocumentJson,
} from "@/lib/product-parse";
import type { CatalogBackend, CatalogStorageInfo } from "@/lib/storage-info";
import type { CatalogDocument, Product } from "@/lib/types";

export type { CatalogBackend, CatalogStorageInfo };

const LOCAL_CATALOG_REL = path.join("data", "live-catalog.json");

function blobConfigured(): boolean {
  return Boolean(process.env.BLOB_READ_WRITE_TOKEN?.trim());
}

function kvClient() {
  const url = process.env.KV_REST_API_URL?.trim();
  const token = process.env.KV_REST_API_TOKEN?.trim();
  if (!url || !token) {
    return null;
  }
  return createClient({ url, token });
}

function kvConfigured(): boolean {
  return kvClient() !== null;
}

function onVercel(): boolean {
  return process.env.VERCEL === "1";
}

function localPersistAllowed(): boolean {
  return !onVercel();
}

export function getCatalogStorageInfo(): CatalogStorageInfo {
  if (blobConfigured()) {
    return { backend: "blob", canWrite: true, canUpload: true };
  }
  if (kvConfigured()) {
    return { backend: "kv", canWrite: true, canUpload: false };
  }
  if (localPersistAllowed()) {
    return { backend: "local", canWrite: true, canUpload: true };
  }
  return { backend: "seed", canWrite: false, canUpload: false };
}

export function getSeedDocument(): CatalogDocument {
  const parsed = parseCatalogDocument(seedCatalog);
  return parseCatalogDocument({
    ...parsed,
    products: applyHubColorNames(parsed.products),
  });
}

export function getSeedProducts(): Product[] {
  return getSeedDocument().products;
}

/**
 * Hub ten always show the real intake files in `public/products/{MA}/`.
 * Stale Blob URLs (AI covers) and another mã’s folder never win on the shop.
 */
export function overlaySeedHubGalleries(document: CatalogDocument): CatalogDocument {
  const seedByMa = new Map(getSeedDocument().products.map((product) => [product.ma, product]));
  return {
    ...document,
    products: document.products.map((product) => {
      const ownImages = product.images.filter((image) => srcBelongsToMa(image.src, product.ma));
      const next =
        ownImages.length === product.images.length ? product : { ...product, images: ownImages };
      const seed = seedByMa.get(product.ma);
      if (seed && isKnownSeedMa(product.ma) && seed.images.length > 0) {
        return { ...next, images: seed.images };
      }
      return next;
    }),
  };
}

function extraDescriptionIsPlaceholder(product: Product): boolean {
  const labels = TYPE_LABELS[product.type];
  const en = product.descriptionEn.trim();
  const vn = product.descriptionVn.trim();
  if (!en && !vn) {
    return false;
  }
  if (en === labels.en && (vn === labels.vn || vn === "")) {
    return true;
  }
  if (vn === labels.vn && (en === labels.en || en === "")) {
    return true;
  }
  return false;
}

/** Hub ten pick up seed garment copy. Extra mãs drop ops / filler — blank if nothing real. */
export function overlayCustomerStockVoice(document: CatalogDocument): CatalogDocument {
  const seedByMa = new Map(getSeedDocument().products.map((product) => [product.ma, product]));
  return {
    ...document,
    products: document.products.map((product) => {
      const seed = seedByMa.get(product.ma);
      if (seed && isKnownSeedMa(product.ma)) {
        return {
          ...product,
          titleEn: seed.titleEn,
          titleVn: seed.titleVn,
          descriptionEn: seed.descriptionEn,
          descriptionVn: seed.descriptionVn,
        };
      }
      const liveCopy = `${product.titleEn} ${product.titleVn} ${product.descriptionEn} ${product.descriptionVn}`;
      if (!customerOpsVoiceHit(liveCopy) && !extraDescriptionIsPlaceholder(product)) {
        return product;
      }
      return {
        ...product,
        descriptionEn: "",
        descriptionVn: "",
      };
    }),
  };
}

function hydrateLiveCatalog(document: CatalogDocument): CatalogDocument {
  const withSeedPhotos = overlaySeedHubGalleries(document);
  const withSeedCopy = overlayCustomerStockVoice(withSeedPhotos);
  return parseCatalogDocument({
    ...withSeedCopy,
    products: applyHubColorNames(withSeedCopy.products).map(applyRecordedHubSourceLink),
  });
}

function localCatalogPath(): string {
  return path.join(process.cwd(), LOCAL_CATALOG_REL);
}

export function createVercelBlobPort(): BlobCatalogPort {
  return {
    async put(pathname, body) {
      const blob = await put(pathname, body, {
        access: "public",
        addRandomSuffix: false,
        allowOverwrite: true,
        contentType: "application/json",
        cacheControlMaxAge: 0,
      });
      return { url: blob.url, downloadUrl: blob.downloadUrl };
    },
    async list(prefix) {
      const blobs: { pathname: string; url: string }[] = [];
      let cursor: string | undefined;
      let pages = 0;
      do {
        const page = await list({ prefix, limit: 100, cursor });
        for (const blob of page.blobs) {
          blobs.push({ pathname: blob.pathname, url: blob.url });
        }
        cursor = page.hasMore ? page.cursor : undefined;
        pages += 1;
      } while (cursor && pages < 8);
      return blobs;
    },
    async fetchJson(url) {
      const response = await fetch(url, {
        cache: "no-store",
        headers: { "Cache-Control": "no-cache", Pragma: "no-cache" },
      });
      if (!response.ok) {
        throw new Error(`Blob catalog fetch failed (${response.status})`);
      }
      return response.json();
    },
    async getJson(pathname) {
      const result = await get(pathname, { access: "public", useCache: false });
      if (!result || result.statusCode !== 200 || !result.stream) {
        return null;
      }
      const text = await new Response(result.stream).text();
      return JSON.parse(text) as unknown;
    },
  };
}

async function readBlobCatalog(): Promise<CatalogDocument | null> {
  if (!blobConfigured()) {
    return null;
  }
  const document = await readCatalogFromBlobPort(createVercelBlobPort());
  return document ? hydrateLiveCatalog(document) : null;
}

async function readKvCatalog(): Promise<CatalogDocument | null> {
  const client = kvClient();
  if (!client) {
    return null;
  }
  const raw = await client.get<unknown>(catalogKvKey());
  if (raw === null || raw === undefined) {
    return null;
  }
  try {
    return hydrateLiveCatalog(parseCatalogDocument(raw));
  } catch (error) {
    const detail = error instanceof Error ? error.message : "invalid catalog.v1";
    throw new CatalogCorruptError(`KV catalog is corrupt and will not fall back to seed. ${detail}`);
  }
}

async function readLocalCatalog(): Promise<CatalogDocument | null> {
  if (!localPersistAllowed()) {
    return null;
  }
  try {
    const text = await readFile(localCatalogPath(), "utf8");
    const raw: unknown = JSON.parse(text);
    try {
      return hydrateLiveCatalog(parseCatalogDocument(raw));
    } catch (error) {
      const detail = error instanceof Error ? error.message : "invalid catalog.v1";
      throw new CatalogCorruptError(
        `Live catalog file is corrupt and will not fall back to seed. ${detail}`,
      );
    }
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return null;
    }
    if (isCatalogCorruptError(error)) {
      throw error;
    }
    throw new CatalogCorruptError(
      `Live catalog file could not be read and will not fall back to seed. ${
        error instanceof Error ? error.message : "read failed"
      }`,
    );
  }
}

async function writeLocalCatalogFile(json: string): Promise<void> {
  const file = localCatalogPath();
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, json, "utf8");
}

function documentsMatch(left: CatalogDocument, right: CatalogDocument): boolean {
  return toCatalogDocumentJson(left) === toCatalogDocumentJson(right);
}

function persistMismatchError(
  prefix: string,
  expected: CatalogDocument,
  actual: CatalogDocument,
): string {
  const diffs = catalogFieldDiffs(expected, actual);
  const detail = diffs.length > 0 ? diffs.join("; ") : "serialized JSON differed";
  return `${prefix} ${detail}`;
}

export type CatalogReadRecord = {
  document: CatalogDocument;
  source: CatalogBackend;
};

/**
 * One catalog. Seed is bootstrap only — if a live document exists (Blob, KV, or
 * local file), that document is the shop and admin source of truth, even when
 * it differs from data/products.json.
 */

/**
 * Stored catalog bytes only (Blob/KV/local) — no shop hydrate overlays.
 * Hub copy / backups must use this so seed photos/prices never stamp live identity.
 */
export async function readStoredCatalogRecord(): Promise<CatalogReadRecord | null> {
  if (blobConfigured()) {
    try {
      const document = await readCatalogFromBlobPort(createVercelBlobPort());
      if (document) {
        return { document: parseCatalogDocument(document), source: "blob" };
      }
    } catch (error) {
      if (isCatalogCorruptError(error)) {
        throw error;
      }
      console.error("Stored Blob catalog read failed.", error);
    }
  }

  const client = kvClient();
  if (client) {
    try {
      const raw = await client.get<unknown>(catalogKvKey());
      if (raw !== null && raw !== undefined) {
        return { document: parseCatalogDocument(raw), source: "kv" };
      }
    } catch (error) {
      if (isCatalogCorruptError(error)) {
        throw error;
      }
      console.error("Stored KV catalog read failed.", error);
    }
  }

  if (localPersistAllowed()) {
    try {
      const text = await readFile(localCatalogPath(), "utf8");
      return { document: parseCatalogDocument(JSON.parse(text) as unknown), source: "local" };
    } catch (error) {
      if (error && typeof error === "object" && "code" in error && (error as { code?: string }).code === "ENOENT") {
        return null;
      }
      if (isCatalogCorruptError(error)) {
        throw error;
      }
      console.error("Stored local catalog read failed.", error);
    }
  }

  return null;
}

export async function readLiveCatalogRecord(): Promise<CatalogReadRecord> {
  try {
    const fromBlob = await readBlobCatalog();
    if (fromBlob) {
      return { document: fromBlob, source: "blob" };
    }
  } catch (error) {
    if (isCatalogCorruptError(error)) {
      throw error;
    }
    console.error("Live Blob catalog read failed; trying KV/local/seed.", error);
  }

  try {
    const fromKv = await readKvCatalog();
    if (fromKv) {
      return { document: fromKv, source: "kv" };
    }
  } catch (error) {
    if (isCatalogCorruptError(error)) {
      throw error;
    }
    console.error("Live KV catalog read failed; trying local/seed.", error);
  }

  try {
    const fromLocal = await readLocalCatalog();
    if (fromLocal) {
      return { document: fromLocal, source: "local" };
    }
  } catch (error) {
    if (isCatalogCorruptError(error)) {
      throw error;
    }
    console.error("Live local catalog read failed; using seed.", error);
  }

  return { document: getSeedDocument(), source: "seed" };
}

export async function readLiveCatalogDocument(): Promise<CatalogDocument> {
  const record = await readLiveCatalogRecord();
  return record.document;
}

export async function readLiveCatalog(): Promise<Product[]> {
  const document = await readLiveCatalogDocument();
  return document.products;
}

export type CatalogWriteResult = {
  document: CatalogDocument;
  catalogSha: string;
  updatedAt: string;
  backend: CatalogBackend;
  blobWritten: boolean;
};

function writeResult(document: CatalogDocument, backend: CatalogBackend): CatalogWriteResult {
  const updatedAt = document.updatedAt;
  if (!updatedAt) {
    throw new Error("Live catalog write missing updatedAt.");
  }
  return {
    document,
    catalogSha: catalogShaOf(document),
    updatedAt,
    backend,
    blobWritten: backend === "blob" || backend === "kv" || backend === "local",
  };
}

export async function writeLiveCatalogDocument(document: CatalogDocument): Promise<CatalogWriteResult> {
  const parsed = stampCatalogUpdatedAt(hydrateLiveCatalog(document));
  const info = getCatalogStorageInfo();
  if (!info.canWrite) {
    throw new Error(
      "Catalog storage is not configured. Set BLOB_READ_WRITE_TOKEN (preferred) or KV_REST_API_URL + KV_REST_API_TOKEN on Vercel.",
    );
  }

  const json = toCatalogDocumentJson(parsed);
  assertCanonicalSerializedCatalog(json);
  assertLiveCatalogIntegrity(parsed.products);

  if (info.backend === "blob") {
    const verified = await writeCatalogToBlobPort(createVercelBlobPort(), parsed, getCatalogBlobPath());
    if (localPersistAllowed()) {
      try {
        await writeLocalCatalogFile(json);
      } catch (error) {
        console.error("Local catalog backup after Blob write failed.", error);
      }
    }
    let record = await readLiveCatalogRecord();
    if (record.source === "seed") {
      for (const delay of BLOB_READBACK_DELAYS_MS) {
        await waitMs(delay === 0 ? 80 : delay);
        record = await readLiveCatalogRecord();
        if (record.source !== "seed") {
          break;
        }
      }
    }
    if (record.source === "seed") {
      throw new Error(
        "Blob write succeeded but the shop is still reading seed. Catalog.v1 was not readable by pathname.",
      );
    }
    if (documentsMatch(parsed, record.document)) {
      return writeResult(record.document, "blob");
    }
    // Pathname get() can lag after overwrite. Put already matched canonical (or clock-stale) bytes.
    return writeResult(verified, "blob");
  }

  if (info.backend === "kv") {
    const client = kvClient();
    if (!client) {
      throw new Error("KV is not configured.");
    }
    await client.set(catalogKvKey(), parsed);
    const verified = await readKvCatalog();
    if (!verified || !documentsMatch(parsed, verified)) {
      throw new Error(
        verified
          ? persistMismatchError("KV write did not round-trip. Catalog was not saved.", parsed, verified)
          : "KV write did not round-trip. Catalog was not saved.",
      );
    }
    return writeResult(verified, "kv");
  }

  if (info.backend === "local") {
    await writeLocalCatalogFile(json);
    const verified = await readLocalCatalog();
    if (!verified || !documentsMatch(parsed, verified)) {
      throw new Error(
        verified
          ? persistMismatchError(
              "Local catalog write did not round-trip. Catalog was not saved.",
              parsed,
              verified,
            )
          : "Local catalog write did not round-trip. Catalog was not saved.",
      );
    }
    return writeResult(verified, "local");
  }

  throw new Error("Catalog storage is not configured.");
}

export async function writeLiveCatalog(products: Product[]): Promise<CatalogWriteResult> {
  const current = await readLiveCatalogDocument();
  return writeLiveCatalogDocument({
    schema: current.schema,
    version: 1,
    siteId: current.siteId,
    products,
    settings: current.settings,
  });
}

function hashedImageFileName(file: File, bytes: Buffer): string {
  const digest = createHash("sha256").update(bytes).digest("hex").slice(0, 12);
  const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, "-").slice(-80) || "image";
  const coverSafe = safeName.replace(/^cover\.(jpe?g|png|webp|svg)$/i, `cover-${digest}.$1`);
  return `${Date.now()}-${digest}-${coverSafe}`;
}

export async function uploadCatalogImage(ma: string, file: File): Promise<string> {
  const info = getCatalogStorageInfo();
  const bytes = Buffer.from(await file.arrayBuffer());
  const stamp = hashedImageFileName(file, bytes);
  if (isInPlaceCoverPath(stamp)) {
    throw new Error("Refusing in-place cover.jpg overwrite. Upload a hashed cover path.");
  }

  if (info.backend === "blob") {
    const pathname = `${catalogImagePrefix(ma)}/${stamp}`;
    const blob = await put(pathname, bytes, {
      access: "public",
      addRandomSuffix: true,
      contentType: file.type || "application/octet-stream",
    });
    return blob.url;
  }

  if (info.backend === "local") {
    const relative = path.join("uploads", ma, stamp);
    const dest = path.join(process.cwd(), "public", relative);
    await mkdir(path.dirname(dest), { recursive: true });
    await writeFile(dest, bytes);
    return `/${relative.split(path.sep).join("/")}`;
  }

  throw new Error("Image upload needs BLOB_READ_WRITE_TOKEN. Paste an image URL instead.");
}

export function storageWriteErrorMessage(): string {
  return "Cannot save: storage is not configured. On Vercel set BLOB_READ_WRITE_TOKEN (or KV). Locally, saves write to data/live-catalog.json.";
}

export type BlobStoreHealth = {
  configured: boolean;
  prefix: string;
  path: string;
  listed: string[];
  schema: string | null;
  catalogSiteId: string | null;
  readable: boolean;
};

/** Read-only Blob prefix inspect. Never writes persist-probe or catalog.v1. */
export async function inspectBlobStoreHealth(): Promise<BlobStoreHealth> {
  const prefix = catalogBlobPrefix();
  const catalogPath = catalogBlobPath();
  const empty: BlobStoreHealth = {
    configured: blobConfigured(),
    prefix,
    path: catalogPath,
    listed: [],
    schema: null,
    catalogSiteId: null,
    readable: false,
  };
  if (!blobConfigured()) {
    return empty;
  }
  try {
    const port = createVercelBlobPort();
    const blobs = await port.list(prefix);
    const listed = blobs.map((blob) => blob.pathname);
    const raw = await readJsonFromBlobPort(port, catalogPath);
    if (raw === null) {
      return { ...empty, configured: true, listed };
    }
    const document = parseCatalogDocument(raw);
    return {
      configured: true,
      prefix,
      path: catalogPath,
      listed,
      schema: document.schema,
      catalogSiteId: document.siteId,
      readable: true,
    };
  } catch (error) {
    console.error("Blob health inspect failed.", error);
    return { ...empty, configured: true };
  }
}
