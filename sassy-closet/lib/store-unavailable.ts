import { NextResponse } from "next/server";
import { INTAKE_DIRECT_LINK_HEADERS } from "@/lib/intake-direct-link-headers";

/** Vietnamese message shown when the durable store (Vercel Blob) can't be read. */
export const STORE_UNAVAILABLE_VI =
  "Kho mã đang không đọc được (Blob bị khóa / lỗi). Không lưu gì lúc này — báo Mini Boss nha.";

/** Short, non-secret reason for logs/UI (never the token or full URL). */
export function storeErrorReason(error: unknown): string {
  const msg = error instanceof Error ? error.message : String(error);
  if (/blocked/i.test(msg)) return "store-blocked";
  if (/\b403\b|forbidden/i.test(msg)) return "forbidden";
  if (/\b401\b|unauthori[sz]ed|token/i.test(msg)) return "auth";
  if (/fetch failed|ECONN|ETIMEDOUT|network/i.test(msg)) return "network";
  return "read-failed";
}

/**
 * 503 JSON for a failed store read. Read-only: no empty-store fallback.
 * Same open-by-link noindex headers as the other data routes, so a Blob-down
 * body is not indexable when a caller forgets to add them. The error text
 * passed in is classified, never copied.
 */
export function storeUnavailableResponse(error: unknown): NextResponse {
  const reason = storeErrorReason(error);
  console.error(`[intake] store read failed: ${reason}`);
  return NextResponse.json(
    { ok: false, error: STORE_UNAVAILABLE_VI, reason, storeUnavailable: true },
    { status: 503, headers: { ...INTAKE_DIRECT_LINK_HEADERS } },
  );
}
