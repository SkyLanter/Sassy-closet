import { NextResponse } from "next/server";
import { KNOWN_SEED_MAS } from "@/lib/catalog-contract";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";
import { PRIVATE_ROBOTS_TAG } from "@/lib/private-robots";
import { refreshShop, warmShopPaths } from "@/lib/refresh-shop";
import { revalidateRequestAuthorized } from "@/lib/revalidate-secret";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET() {
  return NextResponse.json(
    { ok: false, error: "Use POST to revalidate shop paths." },
    { status: 405, headers: { ...NO_STORE_HEADERS, "X-Robots-Tag": PRIVATE_ROBOTS_TAG, Allow: "POST" } },
  );
}

export async function POST(request: Request) {
  if (!revalidateRequestAuthorized(request)) {
    return NextResponse.json(
      { ok: false, error: "Unauthorized." },
      { status: 401, headers: { ...NO_STORE_HEADERS, "X-Robots-Tag": PRIVATE_ROBOTS_TAG } },
    );
  }
  const revalidated = await refreshShop(...KNOWN_SEED_MAS);
  await warmShopPaths(revalidated);
  return NextResponse.json(
    { ok: true, revalidated, blobWritten: false },
    { headers: { ...NO_STORE_HEADERS, "X-Robots-Tag": PRIVATE_ROBOTS_TAG } },
  );
}
