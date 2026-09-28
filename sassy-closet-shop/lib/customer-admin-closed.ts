import { NextResponse } from "next/server";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";

/**
 * Customer shop does not serve catalog admin.
 * Intake writes `sassy-closet-shop/catalog.v1.json` and asks this app to revalidate.
 * The `null` branch is unused. Callers keep their previous bodies so those
 * modules stay typechecked; every HTTP handler returns 404.
 */
export function customerAdminApiClosed(): NextResponse | null {
  return NextResponse.json(
    { ok: false, error: "Not found." },
    {
      status: 404,
      headers: {
        ...NO_STORE_HEADERS,
        "X-Robots-Tag": "noindex, nofollow",
      },
    },
  );
}

export type CustomerAdminProxyDecision = "continue" | "not-found";

/** Pages and admin APIs 404. POST /api/admin/revalidate stays, and checks a secret. */
export function customerAdminProxyDecision(pathname: string): CustomerAdminProxyDecision {
  if (pathname === "/admin" || pathname.startsWith("/admin/")) {
    return "not-found";
  }
  if (pathname === "/api/admin/revalidate") {
    return "continue";
  }
  if (pathname === "/api/admin" || pathname.startsWith("/api/admin/")) {
    return "not-found";
  }
  return "continue";
}
