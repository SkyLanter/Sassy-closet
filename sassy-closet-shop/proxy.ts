import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { encodeShopSearchHeader, SHOP_SEARCH_HEADER } from "@/lib/look-search";
import { canonicalCategoryPath, canonicalMaPath } from "@/lib/ma-url";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const maCanon = canonicalMaPath(pathname);
  if (maCanon) {
    const url = request.nextUrl.clone();
    url.pathname = maCanon;
    return NextResponse.redirect(url, 308);
  }
  const categoryCanon = canonicalCategoryPath(pathname);
  if (categoryCanon) {
    const url = request.nextUrl.clone();
    url.pathname = categoryCanon;
    return NextResponse.redirect(url, 308);
  }

  const requestHeaders = new Headers(request.headers);
  const query = pathname === "/" ? (request.nextUrl.searchParams.get("q") ?? "").trim() : "";
  if (query) {
    requestHeaders.set(SHOP_SEARCH_HEADER, encodeShopSearchHeader(query));
  } else {
    requestHeaders.delete(SHOP_SEARCH_HEADER);
  }

  const response = NextResponse.next({
    request: { headers: requestHeaders },
  });
  response.headers.set("Cache-Control", "private, no-store, no-cache, max-age=0, must-revalidate");
  response.headers.set("CDN-Cache-Control", "private, no-store");
  response.headers.set("Vercel-CDN-Cache-Control", "private, no-store");
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|icon.svg|editorial/|uploads/).*)"],
};
