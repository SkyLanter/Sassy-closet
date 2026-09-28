import { NextResponse } from "next/server";
import { LISTING_STATUS_TIMEOUT_MS, parseListingFile } from "@/lib/listing-status";

export const dynamic = "force-dynamic";

const NO_STORE = { "Cache-Control": "no-store" };

/**
 * Read-only. Intake never writes this file. No Blob token.
 * Unset URL → `{ enabled: false }` so the UI stays as it is today.
 * Any fetch/parse error → `{ items: {} }` with 200 (badges show "Đang chờ bot").
 */
export async function GET() {
  const url = process.env["LISTING_STATUS_URL"]?.trim() ?? "";
  if (!url) {
    return NextResponse.json({ enabled: false, items: {} }, { headers: NO_STORE });
  }
  try {
    const response = await fetch(url, {
      cache: "no-store",
      signal: AbortSignal.timeout(LISTING_STATUS_TIMEOUT_MS),
    });
    if (!response.ok) return emptyItems();
    const json: unknown = await response.json();
    const items = parseListingFile(json);
    if (!items) return emptyItems();
    return NextResponse.json({ enabled: true, items }, { headers: NO_STORE });
  } catch {
    return emptyItems();
  }
}

function emptyItems() {
  return NextResponse.json({ items: {} }, { headers: NO_STORE });
}
