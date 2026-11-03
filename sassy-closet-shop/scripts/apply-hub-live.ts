import path from "node:path";
import { pathToFileURL } from "node:url";
import { applyCatalogHandoff } from "../lib/catalog-handoff";
import { isKnownSeedMa, KNOWN_SEED_MAS } from "../lib/catalog-contract";
import { recordedHubSourceLink } from "../lib/hub-source-links";
import {
  getCatalogStorageInfo,
  getSeedDocument,
  readStoredCatalogRecord,
  writeLiveCatalogDocument,
} from "../lib/catalog-store";
import { asCatalogDocument } from "../lib/product-parse";
import { siteId } from "../lib/site-runtime";
import type { CatalogDocument, Product } from "../lib/types";

/** Copy the hub ten from seed into the sell catalog. Never writes Excel / intake. */
export function hubIncomingFromSeed(seed: CatalogDocument): CatalogDocument {
  const hubIncoming = asCatalogDocument(
    seed.products.filter((product) => isKnownSeedMa(product.ma)),
    seed.settings,
    siteId(),
  );
  if (hubIncoming.products.length !== KNOWN_SEED_MAS.length) {
    throw new Error(`Hub seed must include ${KNOWN_SEED_MAS.length} mãs, got ${hubIncoming.products.length}`);
  }
  return hubIncoming;
}

/**
 * An available hub-ten row keeps its live dollar. Seed cannot raise or lower it.
 * A hold or sold hub row keeps that stored status and price.
 */
export function preserveStoredHubPrices(next: CatalogDocument, stored: CatalogDocument): CatalogDocument {
  const storedByMa = new Map(stored.products.map((product) => [product.ma, product]));
  return {
    ...next,
    products: next.products.map((product) => keepStoredHubSellState(product, storedByMa.get(product.ma))),
  };
}

function keepStoredHubSellState(product: Product, prior: Product | undefined): Product {
  if (!isKnownSeedMa(product.ma) || !prior) {
    return product;
  }
  switch (prior.status) {
    case "available":
      if (typeof prior.priceUsd === "number") {
        return { ...product, priceUsd: prior.priceUsd };
      }
      return product;
    case "hold":
    case "sold":
      return { ...product, status: prior.status, priceUsd: prior.priceUsd };
    default: {
      const _exhaustive: never = prior.status;
      return _exhaustive;
    }
  }
}

/** Do NOT drop A04. Incoming is hub ten only — extras keep live titles/photos. */
export function prepareStoredHubCatalog(stored: CatalogDocument, hubIncoming: CatalogDocument): CatalogDocument {
  const next = applyCatalogHandoff(stored, hubIncoming, "replace", stored.settings);
  return preserveStoredHubPrices(next, stored);
}

/** Staff-link and live-price checks. Call this before any catalog write. */
export function assertHubCopyReady(document: CatalogDocument, stored: CatalogDocument | null): void {
  const hub = document.products.filter((product) => isKnownSeedMa(product.ma));
  if (hub.length !== KNOWN_SEED_MAS.length) {
    throw new Error(`Hub copy must keep ${KNOWN_SEED_MAS.length} mãs, got ${hub.length}`);
  }
  const missingLinks = hub.filter((product) => !product.sourceLink || !recordedHubSourceLink(product.ma));
  if (missingLinks.length > 0) {
    throw new Error(`Hub copy must keep recorded staff links (${missingLinks.map((product) => product.ma).join(",")})`);
  }
  if (!stored) {
    return;
  }
  const storedByMa = new Map(stored.products.map((product) => [product.ma, product]));
  for (const product of hub) {
    const prior = storedByMa.get(product.ma);
    if (!prior) {
      continue;
    }
    assertStoredHubSellState(product, prior);
  }
}

function assertStoredHubSellState(product: Product, prior: Product): void {
  switch (prior.status) {
    case "available":
      if (typeof prior.priceUsd === "number" && product.priceUsd !== prior.priceUsd) {
        throw new Error(`Hub ${product.ma} must keep its live price.`);
      }
      return;
    case "hold":
    case "sold":
      if (product.status !== prior.status || product.priceUsd !== prior.priceUsd) {
        throw new Error(`Hub ${product.ma} must keep its stored ${prior.status} row.`);
      }
      return;
    default: {
      const _exhaustive: never = prior.status;
      return _exhaustive;
    }
  }
}

export async function commitHubCatalog<T>(
  document: CatalogDocument,
  stored: CatalogDocument | null,
  write: (document: CatalogDocument) => Promise<T>,
): Promise<T> {
  assertHubCopyReady(document, stored);
  return write(document);
}

async function main(): Promise<void> {
  const storage = getCatalogStorageInfo();
  if (!storage.canWrite) {
    throw new Error("Live catalog is not writable.");
  }

  const hubIncoming = hubIncomingFromSeed(getSeedDocument());
  const stored = await readStoredCatalogRecord();
  if (!stored) {
    if (storage.backend === "blob" || storage.backend === "kv") {
      throw new Error(
        "Refusing hub copy: Blob/KV configured but no stored catalog. Do not stamp seed floor over live.",
      );
    }
    const written = await commitHubCatalog(hubIncoming, null, writeLiveCatalogDocument);
    console.log(
      `hub live catalog bootstrapped backend=${written.backend} sha=${written.catalogSha} count=${written.document.products.length}`,
    );
    return;
  }

  if (stored.source === "seed") {
    throw new Error("Refusing hub copy from seed-only read — would wipe live Blob margins.");
  }

  const liveA01 = stored.document.products.find((product) => product.ma === "A01");
  if (!liveA01) {
    throw new Error("Refusing hub copy: stored catalog missing A01.");
  }

  const next = prepareStoredHubCatalog(stored.document, hubIncoming);
  const written = await commitHubCatalog(next, stored.document, writeLiveCatalogDocument);
  const extras = written.document.products.filter((product) => !isKnownSeedMa(product.ma));
  console.log(
    `hub live catalog written backend=${written.backend} blobWritten=${written.blobWritten} sha=${written.catalogSha} count=${written.document.products.length} extras=${extras.map((product) => product.ma).join(",") || "none"}`,
  );
}

function isDirectRun(): boolean {
  const entry = process.argv[1];
  if (!entry) {
    return false;
  }
  return pathToFileURL(path.resolve(entry)).href === import.meta.url;
}

if (isDirectRun()) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exit(1);
  });
}
