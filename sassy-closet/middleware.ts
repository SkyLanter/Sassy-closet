import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { ADMIN_SESSION_COOKIE, verifyAdminSession } from "@/lib/admin-auth";
import { safeShopAdminNext, shopAdminGate } from "@/lib/shop-admin-gate";

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = await verifyAdminSession(request.cookies.get(ADMIN_SESSION_COOKIE)?.value ?? "");
  const decision = shopAdminGate(pathname, hasSession);
  if (decision === "public" || decision === "allow") {
    return NextResponse.next();
  }
  if (pathname.startsWith("/api/")) {
    return NextResponse.json(
      { ok: false, error: "Unauthorized." },
      {
        status: 401,
        headers: {
          "Cache-Control": "private, no-store, no-cache, max-age=0, must-revalidate",
          "X-Robots-Tag": "noindex, nofollow",
        },
      },
    );
  }
  const url = request.nextUrl.clone();
  const next = safeShopAdminNext(pathname + request.nextUrl.search);
  url.pathname = "/admin/shop/login";
  url.search = "";
  url.hash = "";
  if (next !== "/admin/shop") {
    url.searchParams.set("next", next);
  }
  const response = NextResponse.redirect(url, 307);
  response.headers.set("Cache-Control", "private, no-store, no-cache, max-age=0, must-revalidate");
  response.headers.set("X-Robots-Tag", "noindex, nofollow");
  return response;
}

export const config = {
  matcher: ["/admin/shop", "/admin/shop/:path*", "/api/shop-catalog", "/api/shop-catalog/:path*"],
};
