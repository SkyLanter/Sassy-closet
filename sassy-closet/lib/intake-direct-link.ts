import { NextResponse } from "next/server";
import { INTAKE_DIRECT_LINK_HEADERS } from "@/lib/intake-direct-link-headers";

export { INTAKE_DIRECT_LINK_HEADERS, INTAKE_DIRECT_LINK_SOURCES } from "@/lib/intake-direct-link-headers";

export function withIntakeDirectLinkHeaders(response: NextResponse): NextResponse {
  for (const [key, value] of Object.entries(INTAKE_DIRECT_LINK_HEADERS)) {
    response.headers.set(key, value);
  }
  return response;
}

export function intakeDirectJson(body: unknown, status = 200, extra?: Record<string, string>): NextResponse {
  return NextResponse.json(body, {
    status,
    headers: { ...INTAKE_DIRECT_LINK_HEADERS, ...extra },
  });
}
