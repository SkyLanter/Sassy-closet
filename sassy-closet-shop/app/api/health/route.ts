import { NextResponse } from "next/server";
import { inspectCatalogIntegrity, isCatalogCorruptError } from "@/lib/catalog-integrity";
import { CATALOG_SCHEMA, KNOWN_SEED_MAS } from "@/lib/catalog-contract";
import { getCatalogStorageInfo, inspectBlobStoreHealth, readLiveCatalogRecord } from "@/lib/catalog-store";
import { catalogPublicSafety } from "@/lib/public-safety";
import { shopVisibleProducts } from "@/lib/site-settings";
import { siteRuntimeInfo } from "@/lib/site-runtime";

export const dynamic = "force-dynamic";

export async function GET() {
  let record;
  try {
    record = await readLiveCatalogRecord();
  } catch (error) {
    const message = error instanceof Error ? error.message : "Catalog read failed";
    return NextResponse.json(
      {
        ok: false,
        error: message,
        corrupt: isCatalogCorruptError(error),
      },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }
  const storage = getCatalogStorageInfo();
  const site = siteRuntimeInfo();
  const blob = await inspectBlobStoreHealth();
  const integrity = inspectCatalogIntegrity(record.document.products);
  const missingKnown = integrity.missingAllowlist;
  const schemaOk = record.document.schema === CATALOG_SCHEMA;
  const publicSafety = catalogPublicSafety(record.document.products);
  const shopFacing = shopVisibleProducts(record.document.products);
  const shopFacingOk = shopFacing.every(
    (product) => product.status === "hold" || product.status === "available",
  );
  const hubMessageReady = KNOWN_SEED_MAS.filter((ma) =>
    shopFacing.some((product) => product.ma === ma),
  ).length;
  const body = {
    ok:
      schemaOk &&
      missingKnown.length === 0 &&
      publicSafety.ok &&
      integrity.duplicates.length === 0 &&
      integrity.officialAlphabet.length === 0 &&
      shopFacingOk &&
      hubMessageReady === KNOWN_SEED_MAS.length,
    schema: record.document.schema,
    siteId: site.id,
    catalogSiteId: record.document.siteId,
    mode: site.mode,
    backend: storage.backend,
    reading: record.source,
    canWrite: storage.canWrite,
    blobConfigured: blob.configured,
    blob: {
      configured: blob.configured,
      prefix: blob.prefix,
      path: blob.path,
      listed: blob.listed,
      schema: blob.schema,
      catalogSiteId: blob.catalogSiteId,
      readable: blob.readable,
    },
    productCount: record.document.products.length,
    shopVisible: shopFacing.length,
    hubMessageReady,
    listed: shopFacing.length,
    extras: integrity.extras,
    duplicates: integrity.duplicates,
    officialAlphabet: integrity.officialAlphabet,
    soldHidden: integrity.soldHidden,
    dropship: record.document.products.filter((product) => product.fulfillment === "dropship").length,
    onHand: record.document.products.filter((product) => product.fulfillment === "on_hand").length,
    sourceLinks: record.document.products.filter((product) => Boolean(product.sourceLink)).length,
    catalogUpdatedAt: record.document.updatedAt ?? null,
    publicSafety,
    knownMas: [...KNOWN_SEED_MAS],
    missingKnown,
  };
  return NextResponse.json(body, {
    status: body.ok ? 200 : 503,
    headers: { "Cache-Control": "no-store" },
  });
}
