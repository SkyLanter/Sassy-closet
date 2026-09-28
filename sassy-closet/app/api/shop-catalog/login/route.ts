import { NextResponse } from "next/server";
import {
  adminAuthConfigured,
  adminSessionCookie,
  createAdminSessionToken,
  passwordMatches,
} from "@/lib/admin-auth";
import {
  clientAddress,
  loginAttemptAllowed,
  recordLoginFailure,
  recordLoginSuccess,
  waitForLoginFailure,
} from "@/lib/admin-login-rate";
import { safeShopAdminNext } from "@/lib/shop-admin-gate";
import { SHOP_ADMIN_NO_STORE, shopAdminJson } from "@/lib/shop-admin-http";

export const dynamic = "force-dynamic";

async function readSubmission(request: Request): Promise<{ password: string; next: string; json: boolean }> {
  const contentType = request.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    let body: unknown = null;
    try {
      body = await request.json();
    } catch {
      body = null;
    }
    const record = typeof body === "object" && body !== null ? (body as Record<string, unknown>) : {};
    return {
      password: typeof record.password === "string" ? record.password : "",
      next: typeof record.next === "string" ? record.next : "",
      json: true,
    };
  }
  try {
    const form = await request.formData();
    const password = form.get("password");
    const next = form.get("next");
    return {
      password: typeof password === "string" ? password : "",
      next: typeof next === "string" ? next : "",
      json: false,
    };
  } catch {
    return { password: "", next: "", json: false };
  }
}

function failResponse(
  request: Request,
  json: boolean,
  status: 401 | 429 | 503,
  next: string,
  retryAfterSeconds?: number,
): NextResponse {
  const error = status === 429 ? "Too many tries." : status === 503 ? "Admin is locked." : "Unauthorized.";
  if (json) {
    return shopAdminJson(
      { ok: false, error },
      status,
      retryAfterSeconds ? { "Retry-After": String(retryAfterSeconds) } : undefined,
    );
  }
  const url = new URL(request.url);
  url.pathname = "/admin/shop/login";
  url.search = "";
  url.hash = "";
  const safe = safeShopAdminNext(next);
  if (safe !== "/admin/shop") {
    url.searchParams.set("next", safe);
  }
  const code = status === 429 ? "slow" : status === 503 ? "closed" : "1";
  url.searchParams.set("e", code);
  const response = NextResponse.redirect(url, 303);
  response.headers.set("X-Robots-Tag", "noindex, nofollow");
  response.headers.set("Cache-Control", SHOP_ADMIN_NO_STORE["Cache-Control"]);
  if (retryAfterSeconds) {
    response.headers.set("Retry-After", String(retryAfterSeconds));
  }
  return response;
}

export async function GET() {
  return shopAdminJson({ ok: false, error: "Use POST to sign in." }, 405, { Allow: "POST" });
}

export async function POST(request: Request) {
  const ip = clientAddress(request);
  const now = Date.now();
  const limit = loginAttemptAllowed(ip, now);
  const submission = await readSubmission(request);
  if (!limit.ok) {
    await waitForLoginFailure();
    return failResponse(request, submission.json, 429, submission.next, limit.retryAfterSeconds);
  }
  if (!adminAuthConfigured()) {
    await waitForLoginFailure();
    return failResponse(request, submission.json, 503, submission.next);
  }
  if (!(await passwordMatches(submission.password))) {
    recordLoginFailure(ip, Date.now());
    await waitForLoginFailure();
    return failResponse(request, submission.json, 401, submission.next);
  }
  const token = await createAdminSessionToken();
  if (!token) {
    await waitForLoginFailure();
    return failResponse(request, submission.json, 503, submission.next);
  }
  recordLoginSuccess(ip);
  if (submission.json) {
    const response = shopAdminJson({ ok: true });
    response.cookies.set(adminSessionCookie(token));
    return response;
  }
  const dest = safeShopAdminNext(submission.next);
  const splitAt = dest.indexOf("?");
  const url = new URL(request.url);
  url.pathname = splitAt === -1 ? dest : dest.slice(0, splitAt);
  url.search = splitAt === -1 ? "" : dest.slice(splitAt);
  url.hash = "";
  const response = NextResponse.redirect(url, 303);
  response.cookies.set(adminSessionCookie(token));
  response.headers.set("X-Robots-Tag", "noindex, nofollow");
  response.headers.set("Cache-Control", SHOP_ADMIN_NO_STORE["Cache-Control"]);
  return response;
}
