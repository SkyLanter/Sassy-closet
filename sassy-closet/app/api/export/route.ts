import { NextResponse } from "next/server";
import { exportCsv } from "@/lib/store";

export async function GET() {
  return new NextResponse(await exportCsv(), {
    headers: {
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": "attachment; filename=sassy-closet.csv",
    },
  });
}
