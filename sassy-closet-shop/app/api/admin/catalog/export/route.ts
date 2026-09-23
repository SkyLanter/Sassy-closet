import { NextResponse } from "next/server";
import { catalogExportFilename } from "@/lib/catalog-contract";
import { assertHandoffJson, toHandoffCatalogJson } from "@/lib/catalog-handoff";
import { getCatalogDocumentUncached } from "@/lib/products";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function POST() {
  return NextResponse.json(
    { ok: false, error: "Use GET to export catalog.v1." },
    { status: 405, headers: { ...NO_STORE_HEADERS, Allow: "GET" } },
  );
}

export async function GET() {
  try {
    const document = await getCatalogDocumentUncached();
    const json = toHandoffCatalogJson(document);
    assertHandoffJson(json);
    const filename = catalogExportFilename(document.siteId);
    return new NextResponse(json, {
      status: 200,
      headers: {
        ...NO_STORE_HEADERS,
        "Content-Type": "application/json; charset=utf-8",
        "Content-Disposition": `attachment; filename="${filename}"`,
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        error: error instanceof Error ? error.message : "Catalog export failed.",
      },
      { status: 500, headers: NO_STORE_HEADERS },
    );
  }
}
