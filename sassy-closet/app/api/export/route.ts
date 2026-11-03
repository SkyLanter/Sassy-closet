import { NextResponse } from "next/server";
import { exportCsv } from "@/lib/store";
import { INTAKE_DIRECT_LINK_HEADERS } from "@/lib/intake-direct-link-headers";
import { withIntakeDirectLinkHeaders } from "@/lib/intake-direct-link";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

// Direct link, no session. CSV stays out of search indexes.
export async function GET() {
  let csv: string;
  try {
    csv = await exportCsv();
  } catch (error) {
    return withIntakeDirectLinkHeaders(storeUnavailableResponse(error));
  }
  return new NextResponse(csv, {
    headers: {
      ...INTAKE_DIRECT_LINK_HEADERS,
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": "attachment; filename=sassy-closet.csv",
    },
  });
}
