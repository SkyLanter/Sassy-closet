import fs from "node:fs";
import path from "node:path";
import { get, put } from "@vercel/blob";
import { clearAskCache } from "./ask-store";
import { asksFile, photosRoot, submissionsFile } from "./paths";
import { clearStoreCache, listSubmissions } from "./store";

const JSON_PREFIX = "sassy-closet";
const SUBMISSIONS_BLOB = `${JSON_PREFIX}/submissions.json`;
const ASKS_BLOB = `${JSON_PREFIX}/asks.json`;

type BlobGetResult = {
  stream?: ReadableStream<Uint8Array> | null;
} | null;

export function blobConfigured(): boolean {
  return Boolean(
    process.env.BLOB_READ_WRITE_TOKEN?.trim() || process.env.BLOB_STORE_ID?.trim(),
  );
}

export async function hydrateSharedStore(): Promise<void> {
  if (!blobConfigured()) return;
  try {
    const submissions = await readBlobText(SUBMISSIONS_BLOB);
    if (submissions) fs.writeFileSync(submissionsFile(), submissions);
    const asks = await readBlobText(ASKS_BLOB);
    if (asks) fs.writeFileSync(asksFile(), asks);
    clearStoreCache();
    clearAskCache();
    await hydrateReferencedPhotos();
  } catch {
    // Stay on the local data dir if Blob is unset or unreachable.
  }
}

export async function persistSharedStore(): Promise<void> {
  if (!blobConfigured()) return;
  try {
    await writeBlobText(SUBMISSIONS_BLOB, readIfExists(submissionsFile()) ?? emptySubmissions());
    await writeBlobText(ASKS_BLOB, readIfExists(asksFile()) ?? '{"asks":[]}');
    await persistReferencedPhotos();
  } catch {
    // Local write already succeeded; shared copy is best-effort.
  }
}

async function hydrateReferencedPhotos(): Promise<void> {
  const root = photosRoot();
  for (const row of listSubmissions()) {
    for (const rel of row.photo_paths) {
      const dest = path.join(root, rel);
      if (!dest.startsWith(root) || fs.existsSync(dest)) continue;
      const bytes = await readBlobBytes(`${JSON_PREFIX}/photos/${rel}`);
      if (!bytes) continue;
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, bytes);
    }
  }
}

async function persistReferencedPhotos(): Promise<void> {
  const root = photosRoot();
  for (const row of listSubmissions()) {
    for (const rel of row.photo_paths) {
      const file = path.join(root, rel);
      if (!file.startsWith(root) || !fs.existsSync(file)) continue;
      await put(`${JSON_PREFIX}/photos/${rel}`, fs.readFileSync(file), {
        access: "private",
        addRandomSuffix: false,
        allowOverwrite: true,
        cacheControlMaxAge: 0,
      });
    }
  }
}

async function readBlobText(pathname: string): Promise<string | null> {
  const bytes = await readBlobBytes(pathname);
  return bytes ? bytes.toString("utf8") : null;
}

async function readBlobBytes(pathname: string): Promise<Buffer | null> {
  const result = (await get(pathname, {
    access: "private",
    useCache: false,
  })) as BlobGetResult;
  if (!result?.stream) return null;
  return Buffer.from(await new Response(result.stream).arrayBuffer());
}

async function writeBlobText(pathname: string, text: string): Promise<void> {
  await put(pathname, text, {
    access: "private",
    addRandomSuffix: false,
    allowOverwrite: true,
    cacheControlMaxAge: 0,
    contentType: "application/json",
  });
}

function readIfExists(file: string): string | null {
  return fs.existsSync(file) ? fs.readFileSync(file, "utf8") : null;
}

function emptySubmissions(): string {
  return JSON.stringify(
    { nextId: 1, submissions: [], fx: { usd_cny: 6.71, updated: "2026-09-07" } },
    null,
    2,
  );
}
