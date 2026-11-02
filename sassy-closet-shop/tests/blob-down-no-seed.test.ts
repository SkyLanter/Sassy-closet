import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import {
  classifyBlobGetStatus,
  readCatalogFromBlobPort,
  vercelBlobGetDisposition,
  writeCatalogToBlobPort,
  type BlobCatalogPort,
} from "../lib/blob-catalog";
import { isCatalogCorruptError } from "../lib/catalog-integrity";
import { catalogBlobLegacyPaths } from "../lib/catalog-contract";
import { afterBlobReadError, readLiveCatalogRecord } from "../lib/catalog-store";
import { parseCatalogDocument } from "../lib/product-parse";
import { siteId } from "../lib/site-runtime";

const PRIMARY = "sassy-closet-shop/catalog.v1.json";

function port(overrides: Partial<BlobCatalogPort>): BlobCatalogPort {
  return {
    async put() {
      return { url: "memory://blob/catalog.v1.json" };
    },
    async list() {
      return [];
    },
    async fetchJson() {
      return null;
    },
    async getJson() {
      return null;
    },
    ...overrides,
  };
}

function minimalA01Catalog() {
  return {
    schema: "catalog.v1" as const,
    version: 1 as const,
    siteId: "sassy-closet-shop",
    products: [
      {
        ma: "A01",
        qty: 1 as const,
        status: "available" as const,
        priceUsd: 27,
        colors: [],
        images: [],
        sizes: [],
        fulfillment: "dropship" as const,
        sourceLink: null,
      },
    ],
  };
}

function liveBlobCatch(source: string): string {
  const start = source.indexOf("async function readLiveCatalogRecordFresh");
  assert.ok(start >= 0, "readLiveCatalogRecordFresh");
  const end = source.indexOf("export async function readLiveCatalogRecord()", start);
  assert.ok(end > start, "readLiveCatalogRecord");
  const fn = source.slice(start, end);
  const blobCall = fn.indexOf("readBlobCatalog()");
  const kvCall = fn.indexOf("readKvCatalog()");
  assert.ok(blobCall >= 0 && kvCall > blobCall);
  const between = fn.slice(blobCall, kvCall);
  const catchAt = between.indexOf("} catch (error)");
  assert.ok(catchAt >= 0, "blob catch");
  return between.slice(catchAt);
}

test("classifyBlobGetStatus: 200 ok, 404 missing, other statuses down", () => {
  assert.equal(classifyBlobGetStatus(200), "ok");
  assert.equal(classifyBlobGetStatus(404), "missing");
  assert.equal(classifyBlobGetStatus(403), "down");
  assert.equal(classifyBlobGetStatus(500), "down");
  assert.equal(classifyBlobGetStatus(null), "down");
  assert.equal(classifyBlobGetStatus(undefined), "down");
});

test("vercel get() null is a 404 miss; 304 and other codes are down", () => {
  assert.equal(vercelBlobGetDisposition(null), "missing");
  assert.equal(vercelBlobGetDisposition(undefined), "missing");
  assert.equal(vercelBlobGetDisposition({ statusCode: 200 }), "ok");
  assert.equal(vercelBlobGetDisposition({ statusCode: 404 }), "missing");
  assert.equal(vercelBlobGetDisposition({ statusCode: 304 }), "down");
  assert.equal(vercelBlobGetDisposition({ statusCode: 403 }), "down");
  assert.equal(vercelBlobGetDisposition({ statusCode: 500 }), "down");
});

test("socket hang up and an empty list reject with a generic blob message", async () => {
  await assert.rejects(
    readCatalogFromBlobPort(
      port({
        async getJson() {
          throw new Error("socket hang up");
        },
        async list() {
          return [];
        },
      }),
      PRIMARY,
    ),
    (error: unknown) => {
      assert.equal(isCatalogCorruptError(error), false);
      assert.ok(error instanceof Error);
      assert.equal(error.message, "Blob catalog read failed");
      return true;
    },
  );
});

test("null getJson and an empty list is a missing catalog", async () => {
  const document = await readCatalogFromBlobPort(
    port({
      async getJson() {
        return null;
      },
      async list() {
        return [];
      },
    }),
    PRIMARY,
  );
  assert.equal(document, null);
});

test("primary socket hang up falls through to a legacy catalog document", async () => {
  assert.equal(siteId(), "sassy-closet-shop");
  const legacyPaths = catalogBlobLegacyPaths();
  assert.deepEqual(legacyPaths, ["sassy-closet-shop/catalog.json"]);
  const raw = minimalA01Catalog();
  const accepted = parseCatalogDocument(raw);
  assert.equal(accepted.products[0]?.ma, "A01");
  assert.equal(accepted.products[0]?.priceUsd, 27);

  const document = await readCatalogFromBlobPort(
    port({
      async getJson(pathname: string) {
        if (pathname === PRIMARY) {
          throw new Error("socket hang up");
        }
        if (legacyPaths.includes(pathname)) {
          return raw;
        }
        return null;
      },
      async list(prefix: string) {
        if (prefix === PRIMARY) {
          return [];
        }
        return [];
      },
    }),
    PRIMARY,
  );

  assert.ok(document);
  assert.equal(document.products.length, 1);
  assert.equal(document.products[0]?.ma, "A01");
  assert.equal(document.products[0]?.priceUsd, 27);
});

test("a down legacy pathname does not block a clean primary miss", async () => {
  const legacyPaths = catalogBlobLegacyPaths();
  assert.ok(legacyPaths.includes("sassy-closet-shop/catalog.json"));
  const document = await readCatalogFromBlobPort(
    port({
      async getJson(pathname: string) {
        if (pathname === PRIMARY) {
          return null;
        }
        if (legacyPaths.includes(pathname)) {
          throw new Error("legacy down");
        }
        return null;
      },
      async list(prefix: string) {
        if (prefix === PRIMARY || legacyPaths.includes(prefix)) {
          return [];
        }
        return [];
      },
    }),
    PRIMARY,
  );
  assert.equal(document, null);
});

test("a down pathname readback does not abort put retries", async () => {
  let stored = "";
  let fetches = 0;
  const document = await writeCatalogToBlobPort(
    port({
      async put(_pathname, body) {
        stored = body;
        return { url: "https://blob.example/catalog.v1.json" };
      },
      async getJson() {
        throw new Error("socket hang up");
      },
      async list() {
        return [];
      },
      async fetchJson() {
        fetches += 1;
        if (fetches < 3) {
          return { stale: true };
        }
        return JSON.parse(stored) as unknown;
      },
    }),
    parseCatalogDocument(minimalA01Catalog()),
    PRIMARY,
  );
  assert.equal(document.products[0]?.ma, "A01");
  assert.equal(document.products[0]?.priceUsd, 27);
  assert.ok(fetches >= 3);
});

test("afterBlobReadError rethrows corrupt and generic-fails when down", () => {
  assert.equal(afterBlobReadError("corrupt"), "rethrow");
  assert.equal(afterBlobReadError("down"), "generic-fail");
});

/** Arguments of the one console.error call. Strings may contain semicolons. */
function consoleErrorArguments(region: string): string[] {
  const start = region.indexOf("console.error(");
  assert.ok(start >= 0, "console.error");
  const args: string[] = [];
  let index = start + "console.error(".length;
  while (index < region.length) {
    while (region[index] === " " || region[index] === "\n") {
      index += 1;
    }
    if (region[index] === ")") {
      break;
    }
    if (region[index] === '"') {
      const end = region.indexOf('"', index + 1);
      assert.ok(end > index);
      args.push(region.slice(index, end + 1));
      index = end + 1;
    } else {
      const relative = region.slice(index).search(/[,)]/);
      assert.ok(relative > 0);
      args.push(region.slice(index, index + relative).trim());
      index += relative;
    }
    while (region[index] === " " || region[index] === "\n") {
      index += 1;
    }
    if (region[index] === ",") {
      index += 1;
      continue;
    }
    assert.equal(region[index], ")");
    break;
  }
  return args;
}

test("live blob catch logs a fixed line and does not pass the error through", () => {
  const source = readFileSync(new URL("../lib/catalog-store.ts", import.meta.url), "utf8");
  const blobCatch = liveBlobCatch(source);
  assert.equal(blobCatch.includes("trying KV/local/seed"), false);
  assert.equal(blobCatch.includes("readKvCatalog"), false);
  assert.match(blobCatch, /afterBlobReadError\(/);
  assert.equal(blobCatch.split("console.error(").length, 2);
  assert.deepEqual(consoleErrorArguments(blobCatch), [
    '"Live Blob catalog read failed; not serving seed."',
  ]);
});

test("unset BLOB_READ_WRITE_TOKEN reads seed and does not throw", async () => {
  const saved: Record<string, string | undefined> = {};
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL/.test(key)) {
      saved[key] = process.env[key];
      delete process.env[key];
    }
  }
  const cwd = process.cwd();
  const tmp = mkdtempSync(path.join(tmpdir(), "blob-down-seed-"));
  const logged: unknown[][] = [];
  const originalError = console.error;
  console.error = (...args: unknown[]) => {
    logged.push(args);
  };
  process.chdir(tmp);
  try {
    assert.equal(process.env.BLOB_READ_WRITE_TOKEN, undefined);
    const record = await readLiveCatalogRecord();
    assert.equal(record.source, "seed");
    assert.ok(record.document.products.length > 0);
    assert.deepEqual(logged, []);
  } finally {
    console.error = originalError;
    process.chdir(cwd);
    for (const key of Object.keys(process.env)) {
      if (/BLOB|KV_|VERCEL/.test(key) && !(key in saved)) {
        delete process.env[key];
      }
    }
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
    rmSync(tmp, { recursive: true, force: true });
  }
});
