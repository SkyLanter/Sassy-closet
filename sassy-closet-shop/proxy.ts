import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { ADMIN_SESSION_COOKIE, clearedAdminSessionCookie, verifyAdminSession } from "@/lib/admin-auth";
import {
  adminGateDecision,
  isAdminApiPath,
  isAdminLogoutApi,
  isAdminPagePath,
  safeAdminNext,
} from "@/lib/admin-gate";
import { encodeShopSearchHeader, SHOP_SEARCH_HEADER } from "@/lib/look-search";
import { canonicalCategoryPath, canonicalMaPath } from "@/lib/ma-url";

const NO_STORE = "private, no-store, no-cache, max-age=0, must-revalidate";

function stamp(response: NextResponse, pathname: string): NextResponse {
  response.headers.set("Cache-Control", NO_STORE);
  response.headers.set("CDN-Cache-Control", "private, no-store");
  response.headers.set("Vercel-CDN-Cache-Control", "private, no-store");
  if (isAdminPagePath(pathname) || isAdminApiPath(pathname)) {
    response.headers.set("X-Robots-Tag", "noindex, nofollow");
  }
  return response;
}

function unauthorized(): NextResponse {
  const response = NextResponse.json(
    { ok: false, error: "Unauthorized." },
    {
      status: 401,
      headers: {
        "Cache-Control": NO_STORE,
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
  );
  response.headers.set("CDN-Cache-Control", "private, no-store");
  response.headers.set("Vercel-CDN-Cache-Control", "private, no-store");
  return response;
}

function redirectToLogin(request: NextRequest): NextResponse {
  const url = request.nextUrl.clone();
  const next = safeAdminNext(request.nextUrl.pathname + request.nextUrl.search);
  url.pathname = "/admin/login";
  url.search = "";
  url.hash = "";
  if (next !== "/admin") {
    url.searchParams.set("next", next);
  }
  return stamp(NextResponse.redirect(url), "/admin/login");
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = verifyAdminSession(request.cookies.get(ADMIN_SESSION_COOKIE)?.value ?? "");

  if (request.headers.has("next-action") && !hasSession) {
    return unauthorized();
  }

  const gate = adminGateDecision(pathname, request.method, hasSession);
  if (gate === "deny") {
    const read = request.method === "GET" || request.method === "HEAD";
    if (isAdminApiPath(pathname) || !read) {
      const response = unauthorized();
      if (isAdminLogoutApi(pathname)) {
        response.cookies.set(clearedAdminSessionCookie());
      }
      return response;
    }
    return redirectToLogin(request);
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
  return stamp(response, pathname);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|icon.svg|editorial/|uploads/).*)"],
};
