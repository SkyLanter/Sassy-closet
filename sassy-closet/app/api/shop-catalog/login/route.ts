import { NextResponse } from "next/server";
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

export async function GET(request: Request) {
  return openDesk(request);
}

/** Old sign-in URL. A password is not checked. */
export async function POST(request: Request) {
  const submission = await readSubmission(request);
  if (submission.json) {
    return shopAdminJson({ ok: true });
  }
  return openDesk(request);
}
