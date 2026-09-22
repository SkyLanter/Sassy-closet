import { NextResponse } from "next/server";
import {
  getCatalogStorageInfo,
  storageWriteErrorMessage,
} from "@/lib/catalog-store";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";
import type { SaveReceipt } from "@/lib/save-commit";

export function adminWriteBlocked(): NextResponse | null {
  if (!getCatalogStorageInfo().canWrite) {
    return NextResponse.json(
      { ok: false, error: storageWriteErrorMessage() },
      { status: 503, headers: NO_STORE_HEADERS },
    );
  }
  return null;
}

export function adminFail(error: string, status = 400): NextResponse {
  return NextResponse.json({ ok: false, error }, { status, headers: NO_STORE_HEADERS });
}

export function adminMethodNotAllowed(allow: string, message: string): NextResponse {
  return NextResponse.json(
    { ok: false, error: message },
    { status: 405, headers: { ...NO_STORE_HEADERS, Allow: allow } },
  );
}

export function adminReceiptResponse(
  receipt: SaveReceipt,
  extra?: Record<string, unknown>,
): NextResponse {
  return NextResponse.json(
    {
      ok: true,
      ma: receipt.ma,
      nextMa: receipt.nextMa,
      renamedTo: receipt.renamedTo,
      blobWritten: receipt.blobWritten,
      catalogSha: receipt.catalogSha,
      updatedAt: receipt.updatedAt,
      revalidated: receipt.revalidated,
      products: receipt.products,
      settings: receipt.settings,
      ...extra,
    },
    { headers: NO_STORE_HEADERS },
  );
}
