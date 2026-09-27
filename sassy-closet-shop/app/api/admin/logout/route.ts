import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { clearedAdminSessionCookie } from "@/lib/admin-auth";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";

export const dynamic = "force-dynamic";
export const revalidate = 0;

function stamp(response: NextResponse): NextResponse {
  response.cookies.set(clearedAdminSessionCookie());
  response.headers.set("X-Robots-Tag", "noindex, nofollow");
  response.headers.set("Cache-Control", NO_STORE_HEADERS["Cache-Control"]);
  response.headers.set("Pragma", "no-cache");
  return response;
}

export async function GET() {
  return NextResponse.json(
    { ok: false, error: "Use POST to sign out." },
    {
      status: 405,
      headers: {
        ...NO_STORE_HEADERS,
        "X-Robots-Tag": "noindex, nofollow",
        Allow: "POST",
      },
    },
  );
}

export async function POST(request: NextRequest) {
  const contentType = request.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return stamp(NextResponse.json({ ok: true }, { headers: NO_STORE_HEADERS }));
  }
  const url = request.nextUrl.clone();
  url.pathname = "/admin/login";
  url.search = "";
  url.hash = "";
  return stamp(NextResponse.redirect(url, 303));
}
