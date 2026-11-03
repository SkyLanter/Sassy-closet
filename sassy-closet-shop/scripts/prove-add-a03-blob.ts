import { messageReadyAddFields } from "../lib/admin-add";
import { addProductToCatalog } from "../lib/admin-ops";
import {
  createMemoryBlobPort,
  getCatalogBlobPath,
  readCatalogFromBlobPort,
  writeCatalogToBlobPort,
} from "../lib/blob-catalog";
import { KNOWN_SEED_MAS, catalogBlobPrefix } from "../lib/catalog-contract";
import { getSeedDocument } from "../lib/catalog-store";
import { cardBuyHint } from "../lib/dropship-copy";
import { applyRecordedHubSourceLink, recordedHubSourceLink } from "../lib/hub-source-links";
import { shopSafeProduct } from "../lib/sell-contract";
import { shopVisibleProducts } from "../lib/site-settings";

function fail(message: string): never {
  throw new Error(message);
}

async function main(): Promise<void> {
  const seedDoc = getSeedDocument();
  const seed = {
    ...seedDoc,
    products: seedDoc.products.map(applyRecordedHubSourceLink),
  };
  const port = createMemoryBlobPort();
  await writeCatalogToBlobPort(port, seed, getCatalogBlobPath());

  const before = await readCatalogFromBlobPort(port, getCatalogBlobPath());
  if (!before || before.products.some((product) => product.ma === "A03")) {
    fail("Blob seed must be the hub ten without A03");
  }
  for (const ma of KNOWN_SEED_MAS) {
    if (!before.products.some((product) => product.ma === ma)) {
      fail(`Blob seed missing hub ${ma}`);
    }
  }

  const added = addProductToCatalog(before.products, "A", messageReadyAddFields("A"));
  if (!added.ok || added.ma !== "A03") {
    fail(`Add A03 to Blob catalog failed: ${added.ok ? added.ma : added.error}`);
  }
  const next = { ...before, products: added.products };
  const written = await writeCatalogToBlobPort(port, next, getCatalogBlobPath());
  const roundtrip = await readCatalogFromBlobPort(port, getCatalogBlobPath());
  if (!roundtrip) {
    fail("Blob read-back after Add A03 returned null");
  }
  if (JSON.stringify(roundtrip.products.map((product) => product.ma)) !==
    JSON.stringify(written.products.map((product) => product.ma))) {
    fail("Blob Add A03 did not round-trip");
  }
  if (!shopVisibleProducts(roundtrip.products).some((product) => product.ma === "A03")) {
    fail("A03 must be shop-visible after Blob Add");
  }
  const a03 = roundtrip.products.find((product) => product.ma === "A03");
  if (!a03 || a03.sourceLink !== null) {
    fail("A03 must not receive an invented staff link");
  }
  if (a03.status !== "hold" || a03.priceUsd !== null || a03.fulfillment !== "dropship") {
    fail("A03 Blob Add must be Hold dropship with no invented USD");
  }
  if (cardBuyHint(a03) !== "Message to buy") {
    fail("A03 must stay Message to buy after Blob Add");
  }
  if (roundtrip.products.some((product) => product.ma === "Q01")) {
    fail("Add A must not invent Q01");
  }
  if (KNOWN_SEED_MAS.length !== 10) {
    fail("Hub allowlist must stay ten mãs");
  }
  for (const ma of KNOWN_SEED_MAS) {
    const product = roundtrip.products.find((row) => row.ma === ma);
    if (!product) {
      fail(`Hub ${ma} dropped from Blob after Add`);
    }
    if (!shopVisibleProducts(roundtrip.products).some((row) => row.ma === ma)) {
      fail(`Hub ${ma} must stay Message-ready on Blob`);
    }
    if (cardBuyHint(product) !== "Message to buy") {
      fail(`Hub ${ma} must stay Message to buy on Blob`);
    }
    if (shopSafeProduct(product).sourceLink !== null) {
      fail(`Customer view must strip sourceLink on ${ma}`);
    }
    if ((ma === "P02" || ma === "P05") && (product.status !== "hold" || product.priceUsd !== null)) {
      fail(`${ma} must stay Hold on Blob`);
    }
    const recorded = recordedHubSourceLink(ma);
    if (!recorded || product.sourceLink !== recorded) {
      fail(`Hub ${ma} must keep the recorded staff source_link on Blob`);
    }
  }

  const listed = await port.list(catalogBlobPrefix());
  if (!listed.some((blob) => blob.pathname.endsWith("catalog.v1.json"))) {
    fail("Blob list must include SITE_ID/catalog.v1.json after Add");
  }

  console.log(
    `Add A03 Blob ok ma=A03 path=${getCatalogBlobPath()} count=${roundtrip.products.length} hub=10 extra=A03`,
  );
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
