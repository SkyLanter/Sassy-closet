import { NextResponse } from "next/server";
import { clearedAdminSessionCookie } from "@/lib/admin-auth";
import { SHOP_ADMIN_NO_STORE, shopAdminJson } from "@/lib/shop-admin-http";

export const dynamic = "force-dynamic";

function clear(response: NextResponse): NextResponse {
  response.cookies.set(clearedAdminSessionCookie());
  return response;
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  url.pathname = "/admin/shop/login";
  url.search = "";
  url.hash = "";
  const response = NextResponse.redirect(url, 303);
  response.headers.set("Cache-Control", SHOP_ADMIN_NO_STORE["Cache-Control"]);
  response.headers.set("X-Robots-Tag", "noindex, nofollow");
  return clear(response);
}

export async function POST(request: Request) {
  const contentType = request.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return clear(shopAdminJson({ ok: true }));
  }
  return GET(request);
}
