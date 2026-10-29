import { NextResponse } from "next/server";
import { requireShopAdmin } from "@/lib/shop-admin-http";
import { exportCsv } from "@/lib/store";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const denied = await requireShopAdmin(request);
  if (denied) {
    return denied;
  }
  return new NextResponse(await exportCsv(), {
    headers: {
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": "attachment; filename=sassy-closet.csv",
    },
  });
}
