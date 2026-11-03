import { NextResponse } from "next/server";
import { intakeCatalog } from "@/lib/kinds";

export async function GET() {
  return NextResponse.json({
    catalog: intakeCatalog(),
  });
}
