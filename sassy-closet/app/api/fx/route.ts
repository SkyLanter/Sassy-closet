import { NextResponse } from "next/server";
import { getFx, setFx } from "@/lib/store";
import { withSharedStore } from "@/lib/with-shared";

export async function GET() {
  return NextResponse.json(await withSharedStore(() => getFx(), "read"));
}

export async function POST(request: Request) {
  let usdCny = NaN;
  try {
    const body = (await request.json()) as { usd_cny?: number };
    usdCny = Number(body.usd_cny);
  } catch {
    usdCny = NaN;
  }
  if (!Number.isFinite(usdCny) || usdCny <= 0) {
    return NextResponse.json(
      { error: "Tỷ giá phải là số dương, vd 6.71" },
      { status: 400 },
    );
  }
  return NextResponse.json(await withSharedStore(() => setFx(usdCny), "write"));
}
