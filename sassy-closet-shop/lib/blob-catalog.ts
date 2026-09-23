import { CatalogCorruptError } from "@/lib/catalog-integrity";
import {
  catalogBlobLegacyPaths,
  catalogBlobPath,
  catalogBlobProbePath,
} from "@/lib/catalog-contract";
import {
  BLOB_READBACK_DELAYS_MS,
  catalogBodyMatches,
  catalogFieldDiffs,
  catalogJsonMatches,
  roundTripMismatchError,
  waitMs,
} from "@/lib/catalog-roundtrip";
import { parseCatalogDocument, toCatalogDocumentJson } from "@/lib/product-parse";
import type { CatalogDocument } from "@/lib/types";

export function getCatalogBlobPath(): string {
  return catalogBlobPath();
}

export function getCatalogBlobProbePath(): string {
  return catalogBlobProbePath();
}

export type BlobObject = {
  pathname: string;
  url: string;
};

export type BlobPutResult = {
  url: string;
  downloadUrl?: string;
};

export type BlobCatalogPort = {
  put(pathname: string, body: string): Promise<BlobPutResult>;
  list(prefix: string): Promise<BlobObject[]>;
  fetchJson(url: string): Promise<unknown>;
  /** Read by pathname — do not depend on list() finding the file. */
  getJson(pathname: string): Promise<unknown | null>;
};

export function createMemoryBlobPort(): BlobCatalogPort & {
  store: Map<string, { body: string; url: string }>;
} {
  const store = new Map<string, { body: string; url: string }>();
  let serial = 0;
  return {
    store,
    async put(pathname, body) {
      serial += 1;
      const url = `memory://blob/${serial}/${pathname}`;
      store.set(pathname, { body, url });
      return { url };
    },
    async list(prefix) {
      const blobs: BlobObject[] = [];
      for (const [pathname, value] of store) {
        if (pathname === prefix || pathname.startsWith(prefix)) {
          blobs.push({ pathname, url: value.url });
        }
      }
      return blobs;
    },
    async fetchJson(url) {
      for (const value of store.values()) {
        if (value.url === url) {
          return JSON.parse(value.body) as unknown;
        }
      }
      throw new Error(`Memory blob missing ${url}`);
    },
    async getJson(pathname) {
      const value = store.get(pathname);
      if (!value) {
        return null;
      }
      return JSON.parse(value.body) as unknown;
    },
  };
}

export function pickCatalogBlob(blobs: BlobObject[], pathname = catalogBlobPath()): BlobObject | undefined {
  const exact = blobs.find((blob) => blob.pathname === pathname);
  if (exact) {
    return exact;
  }
  return blobs.find(
    (blob) =>
      blob.pathname.endsWith("catalog.v1.json") ||
      blob.pathname.endsWith("catalog.json") ||
      blob.pathname.endsWith("persist-probe.json"),
  );
}

export async function readJsonFromBlobPort(
  port: BlobCatalogPort,
  pathname: string,
): Promise<unknown | null> {
  try {
    const direct = await port.getJson(pathname);
    if (direct !== null) {
      return direct;
    }
  } catch {
    // Fall through to list + URL fetch (older stores / list-only ports).
  }
  const blobs = await port.list(pathname);
  const match = pickCatalogBlob(blobs, pathname);
  if (!match) {
    return null;
  }
  return port.fetchJson(match.url);
}

export async function readCatalogFromBlobPort(
  port: BlobCatalogPort,
  pathname = catalogBlobPath(),
): Promise<CatalogDocument | null> {
  const candidates = [pathname, ...catalogBlobLegacyPaths()];
  const seen = new Set<string>();
  for (const candidate of candidates) {
    if (seen.has(candidate)) {
      continue;
    }
    seen.add(candidate);
    const raw = await readJsonFromBlobPort(port, candidate);
    if (raw !== null) {
      try {
        return parseCatalogDocument(raw);
      } catch (error) {
        const detail = error instanceof Error ? error.message : "invalid catalog.v1";
        throw new CatalogCorruptError(
          `Blob catalog at ${candidate} is corrupt and will not fall back to seed. ${detail}`,
        );
      }
    }
  }
  return null;
}

function cacheBustBlobUrl(url: string, token: string): string {
  if (!/^https?:\/\//i.test(url)) {
    return url;
  }
  try {
    const next = new URL(url);
    next.searchParams.set("v", token);
    return next.toString();
  } catch {
    return url;
  }
}

async function tryFetchJson(port: BlobCatalogPort, url: string): Promise<unknown | null> {
  try {
    return await port.fetchJson(url);
  } catch {
    return null;
  }
}

function readBackSources(
  port: BlobCatalogPort,
  pathname: string,
  putUrl: string,
  downloadUrl: string | undefined,
  bustToken: string,
): Array<() => Promise<unknown | null>> {
  const urls = [putUrl];
  if (downloadUrl && downloadUrl !== putUrl) {
    urls.push(downloadUrl);
  }
  const bustedUrls = urls
    .map((url) => cacheBustBlobUrl(url, bustToken))
    .filter((url, index, list) => url !== urls[index] && !urls.includes(url) && list.indexOf(url) === index);

  return [
    async () => {
      try {
        return await port.getJson(pathname);
      } catch {
        return null;
      }
    },
    ...urls.map((url) => async () => tryFetchJson(port, url)),
    ...bustedUrls.map((url) => async () => tryFetchJson(port, url)),
    async () => readJsonFromBlobPort(port, pathname),
  ];
}

function closestReadBack(expectedJson: string, raws: unknown[]): unknown | null {
  let best: unknown | null = raws.length > 0 ? raws[raws.length - 1] : null;
  let bestScore = Number.POSITIVE_INFINITY;
  let expected: CatalogDocument;
  try {
    expected = parseCatalogDocument(JSON.parse(expectedJson) as unknown);
  } catch {
    return best;
  }
  for (const raw of raws) {
    try {
      const score = catalogFieldDiffs(expected, parseCatalogDocument(raw)).length;
      if (score < bestScore) {
        bestScore = score;
        best = raw;
      }
    } catch {
      // Keep the last readable body for the error.
    }
  }
  return best;
}

async function readBackAfterPut(
  port: BlobCatalogPort,
  pathname: string,
  putUrl: string,
  downloadUrl: string | undefined,
  expectedJson: string,
  bustToken: string,
): Promise<{ raw: unknown | null; matched: CatalogDocument | null; bodyMatched: boolean }> {
  const sources = readBackSources(port, pathname, putUrl, downloadUrl, bustToken);
  const raws: unknown[] = [];
  let bodyMatched = false;
  for (const read of sources) {
    const raw = await read();
    if (raw === null) {
      continue;
    }
    raws.push(raw);
    if (catalogJsonMatches(expectedJson, raw)) {
      return { raw, matched: parseCatalogDocument(raw), bodyMatched: true };
    }
    if (catalogBodyMatches(expectedJson, raw)) {
      bodyMatched = true;
    }
  }
  return { raw: closestReadBack(expectedJson, raws), matched: null, bodyMatched };
}

export async function writeCatalogToBlobPort(
  port: BlobCatalogPort,
  document: CatalogDocument,
  pathname = catalogBlobPath(),
): Promise<CatalogDocument> {
  const parsed = parseCatalogDocument(document);
  const json = toCatalogDocumentJson(parsed);
  const putResult = await port.put(pathname, json);
  if (!putResult.url) {
    throw new Error("Blob put returned no URL");
  }

  let lastRaw: unknown | null = null;
  let bodyMatched = false;
  for (const [attempt, delay] of BLOB_READBACK_DELAYS_MS.entries()) {
    await waitMs(delay);
    const result = await readBackAfterPut(
      port,
      pathname,
      putResult.url,
      putResult.downloadUrl,
      json,
      `${attempt}-${Date.now()}`,
    );
    lastRaw = result.raw;
    if (result.matched) {
      return result.matched;
    }
    if (result.bodyMatched) {
      // Stale pathname get() often still has the previous `updatedAt`. The put body is the receipt.
      return parsed;
    }
    bodyMatched = bodyMatched || result.bodyMatched;
  }

  if (bodyMatched) {
    return parsed;
  }
  if (lastRaw === null) {
    throw new Error("Blob write did not round-trip: catalog was not readable after put.");
  }
  throw new Error(roundTripMismatchError(json, lastRaw));
}
