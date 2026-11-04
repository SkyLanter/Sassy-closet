import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { catalogImageFolder } from "@/lib/catalog-image-src";
import { customerAdminProxyDecision } from "@/lib/customer-admin-closed";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";
import { encodeShopSearchHeader, SHOP_SEARCH_HEADER } from "@/lib/look-search";
import { canonicalCategoryPath, canonicalMaPath } from "@/lib/ma-url";
import { isShopPrivateSurface, PRIVATE_ROBOTS_TAG } from "@/lib/private-robots";

/**
 * A held folder under public/products is served before the image route can 404.
 * `%2F` stays one path segment here, so decode it once and check the folder again.
 * The image optimizer then reads that same file without calling this proxy, so
 * the outer `/_next/image?url=` request has to 404 before that read starts.
 */
function heldPublicImage(pathname: string): boolean {
  if (catalogImageFolder(pathname) === "off-live") {
    return true;
  }
  if (!pathname.startsWith("/products/")) {
    return false;
  }
  let decoded: string;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    return false;
  }
  if (decoded === pathname) {
    return false;
  }
  return catalogImageFolder(decoded) === "off-live";
}

function optimizerImageUrl(request: NextRequest): string | null {
  if (request.nextUrl.pathname !== "/_next/image") {
    return null;
  }
  return request.nextUrl.searchParams.get("url");
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (customerAdminProxyDecision(pathname) === "not-found") {
    return new NextResponse(null, {
      status: 404,
      headers: {
        "Cache-Control": "private, no-store, no-cache, max-age=0, must-revalidate",
        "CDN-Cache-Control": "private, no-store",
        "Vercel-CDN-Cache-Control": "private, no-store",
        "X-Robots-Tag": PRIVATE_ROBOTS_TAG,
      },
    });
  }
  const optimizerUrl = optimizerImageUrl(request);
  if (heldPublicImage(pathname) || (optimizerUrl !== null && heldPublicImage(optimizerUrl))) {
    return new NextResponse("Not found", { status: 404, headers: NO_STORE_HEADERS });
  }
  // A live optimizer request stays on the image route. Shop cache headers do not belong on it.
  if (pathname === "/_next/image") {
    return NextResponse.next();
  }
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
  if (isShopPrivateSurface(pathname)) {
    response.headers.set("X-Robots-Tag", PRIVATE_ROBOTS_TAG);
  }
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|favicon.ico|icon.svg|editorial/|uploads/).*)"],
};
