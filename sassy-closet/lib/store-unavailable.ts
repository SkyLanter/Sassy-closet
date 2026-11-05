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

const INTAKE_VALIDATION_STATUSES = new Set([400, 404, 409]);

function errorStatus(error: unknown): number | undefined {
  if (!error || typeof error !== "object" || !("status" in error)) return undefined;
  const status = (error as { status?: unknown }).status;
  return typeof status === "number" ? status : undefined;
}

/**
 * Staff-facing save errors stay 400, 404, or 409 with their own message.
 * A store read/write failure becomes the same 503 as the read routes, without the raw error text.
 */
export function intakeWriteErrorResponse(error: unknown): NextResponse {
  const status = errorStatus(error);
  if (status !== undefined && INTAKE_VALIDATION_STATUSES.has(status)) {
    const message = error instanceof Error && error.message ? error.message : "Chưa lưu được, thử lại nha.";
    return NextResponse.json({ error: message }, { status });
  }
  return storeUnavailableResponse(error);
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
