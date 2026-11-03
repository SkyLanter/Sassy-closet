import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { INTAKE_DIRECT_LINK_HEADERS, isIntakePrivateSurface } from "./lib/intake-direct-link-headers";

/** Direct link. No session and no login redirect. Private surfaces stay noindex. */
export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  if (!isIntakePrivateSurface(request.nextUrl.pathname)) {
    return response;
  }
  for (const [key, value] of Object.entries(INTAKE_DIRECT_LINK_HEADERS)) {
    response.headers.set(key, value);
  }
  return response;
}

export const config = {
  matcher: ["/api/:path*", "/admin", "/admin/:path*"],
};
