import { NextResponse } from "next/server";
import { SHOP_ADMIN_NO_STORE, shopAdminJson } from "@/lib/shop-admin-http";

export const dynamic = "force-dynamic";

/** Old sign-in URL. Shop tools have no password, so this opens the desk. */
export async function GET(request: Request) {
  const url = new URL(request.url);
  url.pathname = "/admin/shop";
  url.search = "";
  url.hash = "";
  const response = NextResponse.redirect(url, 303);
  response.headers.set("Cache-Control", SHOP_ADMIN_NO_STORE["Cache-Control"]);
  response.headers.set("X-Robots-Tag", SHOP_ADMIN_NO_STORE["X-Robots-Tag"]);
  return response;
}

export async function POST(request: Request) {
  const contentType = request.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return shopAdminJson({ ok: true });
  }
  return GET(request);
}
