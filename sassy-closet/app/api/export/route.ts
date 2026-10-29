import { NextResponse } from "next/server";
import { exportCsv } from "@/lib/store";
import { requireShopAdmin, SHOP_ADMIN_NO_STORE } from "@/lib/shop-admin-http";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

// CSV carries costs + source links: admin session required (same as shop tools).
export async function GET(request: Request) {
  const denied = await requireShopAdmin(request);
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
