import { NextResponse } from "next/server";
import { loadShopDatasetRows } from "@/lib/shop-dataset-read";

export const dynamic = "force-dynamic";

const NO_STORE = { "Cache-Control": "no-store" };

/** Read-only shop catalog lanes for the intake list. Does not write Blob. */
export async function GET() {
  const rows = await loadShopDatasetRows();
  return NextResponse.json({ rows }, { headers: NO_STORE });
}
