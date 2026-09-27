import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { safeAdminNext } from "@/lib/admin-gate";
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
import { NO_STORE_HEADERS } from "@/lib/http-no-store";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const ROBOTS = { "X-Robots-Tag": "noindex, nofollow" } as const;

function privateHeaders(extra?: Record<string, string>): HeadersInit {
  return { ...NO_STORE_HEADERS, ...ROBOTS, ...extra };
}

async function readSubmission(request: NextRequest): Promise<{
  password: string;
  next: string;
  json: boolean;
}> {
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
  request: NextRequest,
  json: boolean,
  status: 401 | 429 | 503,
  next: string,
  retryAfterSeconds?: number,
): NextResponse {
  const error =
    status === 429 ? "Too many tries." : status === 503 ? "Admin is locked." : "Unauthorized.";
  if (json) {
    return NextResponse.json(
      { ok: false, error },
      {
        status,
        headers: privateHeaders(
          retryAfterSeconds ? { "Retry-After": String(retryAfterSeconds) } : undefined,
        ),
      },
    );
  }
  const url = request.nextUrl.clone();
  url.pathname = "/admin/login";
  url.search = "";
  url.hash = "";
  const safe = safeAdminNext(next);
  if (safe !== "/admin") {
    url.searchParams.set("next", safe);
  }
  const code = status === 429 ? "slow" : status === 503 ? "closed" : "1";
  url.searchParams.set("e", code);
  const response = NextResponse.redirect(url, 303);
  response.headers.set("X-Robots-Tag", "noindex, nofollow");
  response.headers.set("Cache-Control", NO_STORE_HEADERS["Cache-Control"]);
  if (retryAfterSeconds) {
    response.headers.set("Retry-After", String(retryAfterSeconds));
  }
  return response;
}

export async function GET() {
  return NextResponse.json(
    { ok: false, error: "Use POST to sign in." },
    { status: 405, headers: { ...privateHeaders(), Allow: "POST" } },
  );
}

export async function POST(request: NextRequest) {
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
  if (!passwordMatches(submission.password)) {
    recordLoginFailure(ip, Date.now());
    await waitForLoginFailure();
    return failResponse(request, submission.json, 401, submission.next);
  }
  const token = createAdminSessionToken();
  if (!token) {
    await waitForLoginFailure();
    return failResponse(request, submission.json, 503, submission.next);
  }
  recordLoginSuccess(ip);
  if (submission.json) {
    const response = NextResponse.json({ ok: true }, { headers: privateHeaders() });
    response.cookies.set(adminSessionCookie(token));
    return response;
  }
  const dest = safeAdminNext(submission.next);
  const splitAt = dest.indexOf("?");
  const url = request.nextUrl.clone();
  url.pathname = splitAt === -1 ? dest : dest.slice(0, splitAt);
  url.search = splitAt === -1 ? "" : dest.slice(splitAt);
  url.hash = "";
  const response = NextResponse.redirect(url, 303);
  response.cookies.set(adminSessionCookie(token));
  response.headers.set("X-Robots-Tag", "noindex, nofollow");
  response.headers.set("Cache-Control", NO_STORE_HEADERS["Cache-Control"]);
  return response;
}
