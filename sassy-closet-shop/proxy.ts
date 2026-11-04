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
 * Next decodes the pathname once. Dev then joins that path onto public and
 * collapses duplicate slashes, `.`, and `..`. An encoded slash or dot can land
 * on the file. A `..` that leaves the URL root does not.
 */
function pathAfterOneDecode(pathname: string): string | null {
  let decoded: string;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    return null;
  }
  const segments: string[] = [];
  for (const raw of decoded.split("/")) {
    if (raw === "" || raw === ".") {
      continue;
    }
    if (raw === "..") {
      if (segments.length === 0) {
        return null;
      }
      segments.pop();
      continue;
    }
    segments.push(raw);
  }
  return `/${segments.join("/")}`;
}

function heldPublicImage(pathname: string): boolean {
  if (catalogImageFolder(pathname) === "off-live") {
    return true;
  }
  const normalized = pathAfterOneDecode(pathname);
  if (normalized === null || !normalized.startsWith("/products/")) {
    return false;
  }
  return catalogImageFolder(normalized) === "off-live";
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
  if (heldPublicImage(pathname)) {
    return new NextResponse("Not found", { status: 404, headers: NO_STORE_HEADERS });
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
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|icon.svg|editorial/|uploads/).*)",
    // A dot segment under those prefixes still joins onto public/products in dev.
    "/((?:uploads|editorial|_next/static|_next/image|favicon\\.ico|icon\\.svg).*(?:(?:\\.|%2[Ee]){2}).*)",
  ],
};
