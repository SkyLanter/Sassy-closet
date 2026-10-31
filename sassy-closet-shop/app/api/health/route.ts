import { NextResponse } from "next/server";
import { inspectCatalogIntegrity, isCatalogCorruptError } from "@/lib/catalog-integrity";
import { CATALOG_SCHEMA, KNOWN_SEED_MAS } from "@/lib/catalog-contract";
import { inspectBlobStoreHealth, readLiveCatalogRecord } from "@/lib/catalog-store";
import { catalogPublicSafety } from "@/lib/public-safety";
import { publicShopHealth, SHOP_HEALTH_HEADERS, shopHealthError } from "@/lib/shop-health";
import { shopVisibleProducts } from "@/lib/site-settings";

export const dynamic = "force-dynamic";

export async function GET() {
  let record;
  try {
    record = await readLiveCatalogRecord();
  } catch (error) {
    console.error("Shop health read failed.");
    return NextResponse.json(shopHealthError(isCatalogCorruptError(error)), {
      status: 503,
      headers: SHOP_HEALTH_HEADERS,
    });
  }
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
  const body = publicShopHealth({
    ok:
      schemaOk &&
      missingKnown.length === 0 &&
      publicSafety.ok &&
      integrity.duplicates.length === 0 &&
      integrity.officialAlphabet.length === 0 &&
      shopFacingOk &&
      hubMessageReady === KNOWN_SEED_MAS.length,
    schema: record.document.schema,
    reading: record.source,
    blobConfigured: blob.configured,
    blobReadable: blob.readable,
    productCount: record.document.products.length,
    shopVisible: shopFacing.length,
    hubMessageReady,
    missingKnown,
    knownMas: [...KNOWN_SEED_MAS],
  });
  return NextResponse.json(body, {
    status: body.ok ? 200 : 503,
    headers: SHOP_HEALTH_HEADERS,
  });
}
