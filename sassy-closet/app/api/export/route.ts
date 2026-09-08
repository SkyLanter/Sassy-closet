import { NextResponse } from "next/server";
import { exportCsv } from "@/lib/store";
import { withSharedStore } from "@/lib/with-shared";

export async function GET() {
  return new NextResponse(await withSharedStore(() => exportCsv(), "read"), {
    headers: {
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": "attachment; filename=sassy-closet.csv",
    },
  });
}
