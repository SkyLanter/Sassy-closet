import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/** Shop tools and catalog APIs are direct links. No session, no login redirect. */
export function middleware(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/shop", "/admin/shop/:path*", "/api/shop-catalog", "/api/shop-catalog/:path*"],
};
