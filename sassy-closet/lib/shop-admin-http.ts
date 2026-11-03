import { NextResponse } from "next/server";
import { INTAKE_DIRECT_LINK_HEADERS } from "@/lib/intake-direct-link-headers";

export const SHOP_ADMIN_NO_STORE = INTAKE_DIRECT_LINK_HEADERS;

export function shopAdminJson(body: unknown, status = 200, extra?: Record<string, string>): NextResponse {
  return NextResponse.json(body, {
    status,
    headers: { ...SHOP_ADMIN_NO_STORE, ...extra },
  });
}

/**
 * Kept so older callers compile. Intake no longer returns 401 for a missing session.
 * SHOP_ADMIN_401_EMPTY only describes the unused helper body.
 */
export type ShopAdmin401Mode = "json" | "empty";

export function shopAdmin401Mode(): ShopAdmin401Mode {
  const v = (process.env.SHOP_ADMIN_401_EMPTY ?? "").trim().toLowerCase();
  return v === "1" || v === "true" || v === "yes" ? "empty" : "json";
}

export function shopAdminUnauthorized(mode: ShopAdmin401Mode = shopAdmin401Mode()): NextResponse {
  if (mode === "empty") {
    return new NextResponse(null, { status: 401, headers: { ...SHOP_ADMIN_NO_STORE } });
  }
  return shopAdminJson({ ok: false, error: "Unauthorized." }, 401);
}

/** Direct link. A missing cookie is not a denial. */
export async function requireShopAdmin(
  _request: Request,
  _opts?: { mode?: ShopAdmin401Mode },
): Promise<NextResponse | null> {
  return null;
}
