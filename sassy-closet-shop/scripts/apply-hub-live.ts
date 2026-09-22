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

/** Copy the hub ten from seed into the sell catalog. Never writes Excel / intake. */
async function main(): Promise<void> {
  const storage = getCatalogStorageInfo();
  if (!storage.canWrite) {
    throw new Error("Live catalog is not writable.");
  }

  const seed = getSeedDocument();
  const hubIncoming = asCatalogDocument(
    seed.products.filter((product) => isKnownSeedMa(product.ma)),
    seed.settings,
    siteId(),
  );
  if (hubIncoming.products.length !== KNOWN_SEED_MAS.length) {
    throw new Error(`Hub seed must include ${KNOWN_SEED_MAS.length} mãs, got ${hubIncoming.products.length}`);
  }

  const stored = await readStoredCatalogRecord();
  if (!stored) {
    if (storage.backend === "blob" || storage.backend === "kv") {
      throw new Error(
        "Refusing hub copy: Blob/KV configured but no stored catalog. Do not stamp seed floor over live.",
      );
    }
    // Local bootstrap only
    const written = await writeLiveCatalogDocument(hubIncoming);
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

  // Do NOT drop A04. Incoming is hub ten only — extras keep live titles/photos.
  const next = applyCatalogHandoff(stored.document, hubIncoming, "replace", stored.document.settings);

  // Hard guard: never stamp seed floor under live Blob margin prices for hub ten
  const storedByMa = new Map(stored.document.products.map((product) => [product.ma, product]));
  next.products = next.products.map((product) => {
    if (!isKnownSeedMa(product.ma)) {
      return product;
    }
    const prior = storedByMa.get(product.ma);
    if (
      prior &&
      prior.status === "available" &&
      product.status === "available" &&
      typeof prior.priceUsd === "number" &&
      typeof product.priceUsd === "number" &&
      product.priceUsd < prior.priceUsd
    ) {
      return { ...product, priceUsd: prior.priceUsd };
    }
    return product;
  });

  const written = await writeLiveCatalogDocument(next);
  const extras = written.document.products.filter((product) => !isKnownSeedMa(product.ma));
  const hub = written.document.products.filter((product) => isKnownSeedMa(product.ma));
  if (hub.length !== 10) {
    throw new Error(`Hub copy must keep 10 mãs, got ${hub.length}`);
  }
  const missingLinks = hub.filter((product) => !product.sourceLink || !recordedHubSourceLink(product.ma));
  if (missingLinks.length > 0) {
    throw new Error(`Hub copy must keep recorded staff links (${missingLinks.map((product) => product.ma).join(",")})`);
  }
  const holds = hub.filter((product) => product.ma === "P02" || product.ma === "P05");
  if (holds.some((product) => product.status !== "hold" || product.priceUsd !== null)) {
    throw new Error("P02/P05 must stay Hold / Inbox — do not copy a hub sell dollar");
  }
  console.log(
    `hub live catalog written backend=${written.backend} blobWritten=${written.blobWritten} sha=${written.catalogSha} count=${written.document.products.length} extras=${extras.map((product) => product.ma).join(",") || "none"}`,
  );
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
