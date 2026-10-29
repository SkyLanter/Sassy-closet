import { NextResponse } from "next/server";
import { requestHasAdminSession } from "@/lib/admin-auth";
import { pipelineBearerOk } from "@/lib/pipeline-auth";

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

/**
 * 401 body mode for gated shop/intake routes.
 * Default "json" keeps `{ ok:false, error:"Unauthorized." }` (matches middleware).
 * Set env SHOP_ADMIN_401_EMPTY=1 (Boss choice) for a truly empty 401 body.
 * Only the response body changes; who is authorized never changes.
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

/** Session cookie only. The pipeline bearer is not a shop-admin session. */
export async function requireShopAdmin(
  request: Request,
  opts?: { mode?: ShopAdmin401Mode },
): Promise<NextResponse | null> {
  if (await requestHasAdminSession(request)) {
    return null;
  }
  return shopAdminUnauthorized(opts?.mode);
}

/**
 * Shop-admin session, or a machine GET with `Authorization: Bearer $INTAKE_PIPELINE_SECRET`.
 * POST and PATCH ignore the bearer, so the token cannot save a mã.
 */
export async function requireIntakeRead(
  request: Request,
  opts?: { mode?: ShopAdmin401Mode },
): Promise<NextResponse | null> {
  if (await requestHasAdminSession(request)) {
    return null;
  }
  if (request.method === "GET" && (await pipelineBearerOk(request))) {
    return null;
  }
  return shopAdminUnauthorized(opts?.mode);
}
