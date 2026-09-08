import { NextResponse } from "next/server";
import { getFx, setFx } from "@/lib/store";

export async function GET() {
  return NextResponse.json(getFx());
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
  return NextResponse.json(setFx(usdCny));
}
