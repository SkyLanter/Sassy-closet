import { NextResponse } from "next/server";
import { catalogShaOf } from "@/lib/catalog-sha";
import { readLiveCatalogRecord } from "@/lib/catalog-store";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";
import { catalogProductsInOrder } from "@/lib/sell-contract";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET() {
  const record = await readLiveCatalogRecord();
  const products = catalogProductsInOrder(record.document.products);
  const body = {
    products,
    catalogSha: catalogShaOf(record.document),
    updatedAt: record.document.updatedAt ?? null,
    siteId: record.document.siteId,
    schema: record.document.schema,
    source: record.source,
  };
  return NextResponse.json(body, { headers: NO_STORE_HEADERS });
}
