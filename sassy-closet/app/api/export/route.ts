import { NextResponse } from "next/server";
import { exportCsv } from "@/lib/store";
import { requireIntakeRead, SHOP_ADMIN_NO_STORE } from "@/lib/shop-admin-http";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

export const dynamic = "force-dynamic";

// CSV carries costs + source links. GET: shop-admin session or pipeline bearer.
// Middleware also checks this path. See docs/INTAKE_PIPELINE.md.
export async function GET(request: Request) {
  const denied = await requireIntakeRead(request);
  if (denied) return denied;
  let csv: string;
  try {
    csv = await exportCsv();
  } catch (error) {
    return storeUnavailableResponse(error);
  }
  return new NextResponse(csv, {
    headers: {
      ...SHOP_ADMIN_NO_STORE,
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": "attachment; filename=sassy-closet.csv",
    },
  });
}
