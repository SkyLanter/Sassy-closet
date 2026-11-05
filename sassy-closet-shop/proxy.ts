import path from "node:path";
import { fileURLToPath } from "node:url";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { catalogImageFolder } from "@/lib/catalog-image-src";
import { customerAdminProxyDecision } from "@/lib/customer-admin-closed";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";
import { encodeShopSearchHeader, SHOP_SEARCH_HEADER } from "@/lib/look-search";
import { canonicalCategoryPath, canonicalMaPath } from "@/lib/ma-url";
import { isShopPrivateSurface, PRIVATE_ROBOTS_TAG } from "@/lib/private-robots";

const sourceShopDir = path.posix.dirname(fileURLToPath(import.meta.url));

/**
 * A held folder under public/products is served before the image route can 404.
 * Next decodes the pathname once. Dev joins that path onto the real public
 * directory and collapses `.` and `..`. A `..` that leaves the URL root can
 * walk back through the shop directory name and `public`. The shop directory
 * is the project cwd, and also the directory beside this file when the
 * process was started one level up.
 */
function publicRootFrom(dir: string): string[] {
  const normalized = dir.replaceAll("\\", "/").replace(/\/+$/, "");
  const root =
    normalized.length === 0
      ? "/public"
      : normalized.endsWith("/public")
        ? normalized
        : `${normalized}/public`;
  return root.split("/").filter((segment) => segment.length > 0);
}

function shopPublicRoots(): string[][] {
  let cwd = "";
  if (typeof process !== "undefined" && typeof process.cwd === "function") {
    cwd = process.cwd();
  }
  const cwdPosix = cwd.replaceAll("\\", "/").replace(/\/+$/, "");
  const shopName = path.posix.basename(sourceShopDir);
  const dirs = [cwd, sourceShopDir, `${cwdPosix}/${shopName}`];
  const seen = new Set<string>();
  const roots: string[][] = [];
  for (const dir of dirs) {
    const root = publicRootFrom(dir);
    const key = root.join("/");
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    roots.push(root);
  }
  return roots;
}

function joinedUnderRoot(decoded: string, root: readonly string[]): string | null {
  const segments = [...root];
  for (const raw of decoded.split("/")) {
    if (raw === "" || raw === ".") {
      continue;
    }
    if (raw === "..") {
      segments.pop();
      continue;
    }
    segments.push(raw);
  }
  if (segments.length < root.length) {
    return null;
  }
  for (let index = 0; index < root.length; index += 1) {
    if (segments[index] !== root[index]) {
      return null;
    }
  }
  return `/${segments.slice(root.length).join("/")}`;
}

function heldPathAfterDevJoin(pathname: string): string | null {
  let decoded: string;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    return null;
  }
  for (const root of shopPublicRoots()) {
    const normalized = joinedUnderRoot(decoded, root);
    if (
      normalized !== null &&
      normalized.startsWith("/products/") &&
      catalogImageFolder(normalized) === "off-live"
    ) {
      return normalized;
    }
  }
  return null;
}

function heldPublicImage(pathname: string): boolean {
  if (catalogImageFolder(pathname) === "off-live") {
    return true;
  }
  return heldPathAfterDevJoin(pathname) !== null;
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
