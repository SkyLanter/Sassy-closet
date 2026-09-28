import { NextResponse } from "next/server";
import { requestHasAdminSession } from "@/lib/admin-auth";

export const SHOP_ADMIN_NO_STORE = {
  "Cache-Control": "private, no-store, no-cache, max-age=0, must-revalidate",
  "X-Robots-Tag": "noindex, nofollow",
} as const;

export function shopAdminJson(body: unknown, status = 200, extra?: Record<string, string>): NextResponse {
  return NextResponse.json(body, {
    status,
    headers: { ...SHOP_ADMIN_NO_STORE, ...extra },
  });
}

export async function requireShopAdmin(request: Request): Promise<NextResponse | null> {
  if (await requestHasAdminSession(request)) {
    return null;
  }
  return shopAdminJson({ ok: false, error: "Unauthorized." }, 401);
}
