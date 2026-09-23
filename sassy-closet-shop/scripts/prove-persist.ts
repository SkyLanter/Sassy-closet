import { copyFile, unlink } from "node:fs/promises";
import path from "node:path";
import {
  createMemoryBlobPort,
  getCatalogBlobPath,
  getCatalogBlobProbePath,
  readCatalogFromBlobPort,
  writeCatalogToBlobPort,
  type BlobCatalogPort,
} from "../lib/blob-catalog";
import { catalogFieldDiffs, roundTripMismatchError } from "../lib/catalog-roundtrip";
import { emptyFitCm } from "../lib/asia-size";
import { CATALOG_SCHEMA, catalogBlobPath, catalogKvKey } from "../lib/catalog-contract";
import {
  createVercelBlobPort,
  getCatalogStorageInfo,
  getSeedDocument,
  readLiveCatalogDocument,
  writeLiveCatalogDocument,
} from "../lib/catalog-store";
import { asCatalogDocument, assertCanonicalSerializedCatalog, parseCatalogDocument, toCatalogDocumentJson } from "../lib/product-parse";
import { siteId } from "../lib/site-runtime";
import type { CatalogDocument, Product } from "../lib/types";

function fail(message: string): never {
  throw new Error(message);
}

function assertCanonicalProduct(product: Product): void {
  if (!Array.isArray(product.colors)) {
    fail(`${product.ma} missing colors array`);
  }
  if (!Array.isArray(product.sizes)) {
    fail(`${product.ma} missing sizes array`);
  }
  if (!product.fitCm || typeof product.fitCm !== "object") {
    fail(`${product.ma} missing fitCm`);
  }
  for (const image of product.images) {
    if (typeof image.src !== "string") {
      fail(`${product.ma} image missing src`);
    }
    if (image.colorId !== null && typeof image.colorId !== "string") {
      fail(`${product.ma} image colorId must be string or null`);
    }
    if (typeof image.order !== "number" || !Number.isFinite(image.order) || image.order < 1) {
      fail(`${product.ma} image needs a positive order`);
    }
  }
}

async function proveMemoryBlob(seed: CatalogDocument): Promise<void> {
  const port = createMemoryBlobPort();
  const empty = await readCatalogFromBlobPort(port);
  if (empty !== null) {
    fail("Empty memory blob should read as null");
  }

  const written = await writeCatalogToBlobPort(port, seed, getCatalogBlobPath());
  if (written.products.length !== seed.products.length) {
    fail("Memory blob lost products");
  }
  const json = toCatalogDocumentJson(written);
  assertCanonicalSerializedCatalog(json);
  if (written.schema !== CATALOG_SCHEMA || !written.siteId) {
    fail("Memory blob lost catalog.v1 envelope");
  }

  const mutated: CatalogDocument = {
    ...written,
    products: written.products.map((product) =>
      product.ma === "A01" ? { ...product, titleEn: "Top — blob-probe" } : product,
    ),
  };
  await writeCatalogToBlobPort(port, mutated, getCatalogBlobPath());
  const again = await readCatalogFromBlobPort(port, getCatalogBlobPath());
  if (!again) {
    fail("Memory blob read after overwrite returned null");
  }
  if (again.products.find((product) => product.ma === "A01")?.titleEn !== "Top — blob-probe") {
    fail("Memory blob overwrite did not round-trip title");
  }
  if (toCatalogDocumentJson(again) !== toCatalogDocumentJson(mutated)) {
    fail("Memory blob second write mismatch");
  }
}

function kitProveA03(): Product {
  return {
    ma: "A03",
    type: "A",
    titleEn: "Kit prove top",
    titleVn: "Áo",
    priceUsd: null,
    qty: 1,
    status: "hold",
    colors: [],
    images: [],
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionEn: "",
    descriptionVn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

async function proveA03ExtraRoundTrip(seed: CatalogDocument): Promise<void> {
  const extra = kitProveA03();
  const document = asCatalogDocument([...seed.products, extra], seed.settings, seed.siteId, "2026-09-10T05:00:00.000Z");
  const port = createMemoryBlobPort();
  const written = await writeCatalogToBlobPort(port, document);
  const a03 = written.products.find((product) => product.ma === "A03");
  if (!a03 || a03.titleEn !== "Kit prove top" || a03.titleVn !== "Áo") {
    fail("Memory blob must round-trip Edit A03 identity");
  }
  if (toCatalogDocumentJson(written) !== toCatalogDocumentJson(document)) {
    fail("A03 extra catalog JSON must be stable under Blob write/read");
  }
}

function jsonClone(document: CatalogDocument): unknown {
  return JSON.parse(toCatalogDocumentJson(document)) as unknown;
}

async function proveStaleBlobGetRecovers(seed: CatalogDocument): Promise<void> {
  const fresh = parseCatalogDocument({
    ...seed,
    products: seed.products.map((product) =>
      product.ma === "A01" ? { ...product, titleEn: "Kit prove top" } : product,
    ),
    updatedAt: "2026-09-10T05:00:00.000Z",
  });
  const staleBody = jsonClone(seed);
  const freshBody = jsonClone(fresh);
  let gets = 0;
  const port: BlobCatalogPort = {
    async put() {
      return { url: "https://blob.example/sassy-closet-shop/catalog.v1.json" };
    },
    async list() {
      return [];
    },
    async fetchJson() {
      return freshBody;
    },
    async getJson() {
      gets += 1;
      return gets === 1 ? staleBody : freshBody;
    },
  };
  const written = await writeCatalogToBlobPort(port, fresh);
  if (written.products.find((product) => product.ma === "A01")?.titleEn !== "Kit prove top") {
    fail("Stale Blob get() must not fail a Save whose put body already matches");
  }
}

async function proveStaleUpdatedAtStillReceipts(seed: CatalogDocument): Promise<void> {
  const fresh = parseCatalogDocument({
    ...seed,
    updatedAt: "2026-09-10T05:00:00.000Z",
  });
  const staleBody = jsonClone(
    parseCatalogDocument({
      ...seed,
      updatedAt: "2026-09-01T00:00:00.000Z",
    }),
  );
  const port: BlobCatalogPort = {
    async put() {
      return { url: "https://blob.example/sassy-closet-shop/catalog.v1.json" };
    },
    async list() {
      return [];
    },
    async fetchJson() {
      return staleBody;
    },
    async getJson() {
      return staleBody;
    },
  };
  const written = await writeCatalogToBlobPort(port, fresh);
  if (written.updatedAt !== "2026-09-10T05:00:00.000Z") {
    fail("Clock-stale Blob get() must still receipt the catalog that was put");
  }
}

async function proveBlobMismatchNamesFields(seed: CatalogDocument): Promise<void> {
  const wanted = parseCatalogDocument({
    ...seed,
    products: seed.products.map((product) =>
      product.ma === "A01" ? { ...product, titleEn: "Kit prove top" } : product,
    ),
    updatedAt: "2026-09-10T05:00:00.000Z",
  });
  const staleBody = jsonClone(seed);
  const port: BlobCatalogPort = {
    async put() {
      return { url: "memory://blob/catalog.v1.json" };
    },
    async list() {
      return [];
    },
    async fetchJson() {
      return staleBody;
    },
    async getJson() {
      return staleBody;
    },
  };
  try {
    await writeCatalogToBlobPort(port, wanted);
    fail("Always-stale Blob read-back must not look like a Save");
  } catch (error) {
    const message = error instanceof Error ? error.message : "";
    if (!message.includes("products[A01].titleEn") || !message.includes("Kit prove top")) {
      fail(`Mismatch error must name titleEn, got ${message}`);
    }
  }
  const diffs = catalogFieldDiffs(wanted, seed);
  if (!diffs.some((line) => line.includes("products[A01].titleEn"))) {
    fail("catalogFieldDiffs must name products[A01].titleEn");
  }
  const formatted = roundTripMismatchError(toCatalogDocumentJson(wanted), staleBody);
  if (!formatted.includes("products[A01].titleEn")) {
    fail("roundTripMismatchError must name the differing key");
  }
}

async function proveLocalFile(seed: CatalogDocument): Promise<void> {
  const info = getCatalogStorageInfo();
  if (info.backend !== "local") {
    console.log(`local persist skip (backend=${info.backend})`);
    return;
  }

  const livePath = path.join(process.cwd(), "data", "live-catalog.json");
  const backupPath = `${livePath}.persist-bak`;
  let hadLive = false;
  try {
    await copyFile(livePath, backupPath);
    hadLive = true;
  } catch {
    hadLive = false;
  }

  try {
    await unlink(livePath).catch(() => undefined);

    const before = await readLiveCatalogDocument();
    if (toCatalogDocumentJson(before) !== toCatalogDocumentJson(seed)) {
      fail("With no live file, read should equal seed");
    }

    const probe = asCatalogDocument(
      [
        ...seed.products.map((product) =>
          product.ma === "A01" ? { ...product, titleEn: "Top — persist-probe" } : product,
        ),
        kitProveA03(),
      ],
      seed.settings,
    );

    const written = await writeLiveCatalogDocument(probe);
    const roundtrip = await readLiveCatalogDocument();
    assertCanonicalSerializedCatalog(toCatalogDocumentJson(roundtrip));
    if (!roundtrip.updatedAt) {
      fail("Live write must stamp updatedAt");
    }
    const diffs = catalogFieldDiffs(written.document, roundtrip);
    if (diffs.length > 0) {
      fail(`Local live-catalog.json did not round-trip: ${diffs.join("; ")}`);
    }
    const a01 = roundtrip.products.find((product) => product.ma === "A01");
    if (!a01 || a01.titleEn === "Top — persist-probe") {
      fail("Hub overlay must restore seed A01 title on write (extras keep Edit identity)");
    }
    const a03 = roundtrip.products.find((product) => product.ma === "A03");
    if (!a03 || a03.titleEn !== "Kit prove top" || a03.titleVn !== "Áo") {
      fail("Local round-trip lost Edit A03 identity");
    }
  } finally {
    if (hadLive) {
      await copyFile(backupPath, livePath);
      await unlink(backupPath).catch(() => undefined);
    } else {
      await unlink(livePath).catch(() => undefined);
      await unlink(backupPath).catch(() => undefined);
    }
  }
}

async function proveLiveBlobIfConfigured(seed: CatalogDocument): Promise<void> {
  if (!process.env.BLOB_READ_WRITE_TOKEN?.trim()) {
    console.log("live Blob skip (no BLOB_READ_WRITE_TOKEN in this environment)");
    return;
  }
  const port = createVercelBlobPort();
  const probe = asCatalogDocument(seed.products.slice(0, 1), seed.settings);
  await writeCatalogToBlobPort(port, probe, getCatalogBlobProbePath());
  const read = await readCatalogFromBlobPort(port, getCatalogBlobProbePath());
  if (!read || read.products[0]?.ma !== seed.products[0]?.ma) {
    fail("Live Blob probe put/list/fetch failed");
  }
  console.log("live Blob probe put/list/fetch ok");
}

async function main() {
  const seed = getSeedDocument();
  if (seed.schema !== CATALOG_SCHEMA || seed.version !== 1) {
    fail("Seed document must be catalog.v1");
  }
  if (seed.products.length !== 10) {
    fail(`Seed must have 10 mãs, got ${seed.products.length}`);
  }
  for (const product of seed.products) {
    assertCanonicalProduct(product);
  }
  assertCanonicalSerializedCatalog(toCatalogDocumentJson(seed));

  const parsedAgain = parseCatalogDocument(JSON.parse(toCatalogDocumentJson(seed)) as unknown);
  if (toCatalogDocumentJson(parsedAgain) !== toCatalogDocumentJson(seed)) {
    fail("Seed JSON is not stable under parse");
  }
  if (catalogBlobPath() !== `${siteId()}/catalog.v1.json`) {
    fail("Blob path must be SITE_ID/catalog.v1.json");
  }
  if (catalogKvKey() !== `${siteId()}:catalog.v1`) {
    fail("KV key must be SITE_ID:catalog.v1");
  }

  await proveMemoryBlob(seed);
  await proveStaleBlobGetRecovers(seed);
  await proveStaleUpdatedAtStillReceipts(seed);
  await proveBlobMismatchNamesFields(seed);
  await proveA03ExtraRoundTrip(seed);
  await proveLocalFile(seed);
  await proveLiveBlobIfConfigured(seed);

  console.log("persist smoke ok", {
    backend: getCatalogStorageInfo().backend,
    siteId: siteId(),
    blobPath: getCatalogBlobPath(),
    seedMas: seed.products.map((product) => product.ma).join(","),
  });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
