import { NextResponse } from "next/server";
import { SHOP_ADMIN_NO_STORE, shopAdminJson } from "@/lib/shop-admin-http";

export const dynamic = "force-dynamic";

function openDesk(request: Request): NextResponse {
  const url = new URL(request.url);
  url.pathname = "/admin/shop";
  url.search = "";
  url.hash = "";
  const response = NextResponse.redirect(url, 303);
  response.headers.set("X-Robots-Tag", SHOP_ADMIN_NO_STORE["X-Robots-Tag"]);
  response.headers.set("Cache-Control", SHOP_ADMIN_NO_STORE["Cache-Control"]);
  return response;
}

/** Old sign-in URL. Shop tools have no password. */
export async function GET(request: Request) {
  return openDesk(request);
}

export async function POST(request: Request) {
  const contentType = request.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return shopAdminJson({ ok: true });
  }
  return openDesk(request);
}
