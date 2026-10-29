import { NextResponse } from "next/server";
import { SHOP_ADMIN_NO_STORE, requireShopAdmin } from "@/lib/shop-admin-http";
import { exportCsv } from "@/lib/store";

export async function GET(request: Request) {
  const denied = await requireShopAdmin(request);
  if (denied) {
    return denied;
  }
  return new NextResponse(await exportCsv(), {
    headers: {
      ...SHOP_ADMIN_NO_STORE,
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": "attachment; filename=sassy-closet.csv",
    },
  });
}
