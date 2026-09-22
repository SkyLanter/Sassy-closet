import {
  applyCatalogHandoff,
  parseHandoffCatalog,
  settingsForHandoffImport,
} from "@/lib/catalog-handoff";
import {
  adminFail,
  adminMethodNotAllowed,
  adminReceiptResponse,
  adminWriteBlocked,
} from "@/lib/admin-json-response";
import { asCatalogDocument, assertCanonicalSerializedCatalog, toCatalogDocumentJson } from "@/lib/product-parse";
import { getCatalogDocumentUncached } from "@/lib/products";
import { commitCatalogDocument } from "@/lib/save-commit";
import { assertImportSellContract } from "@/lib/sell-contract";
import { siteId } from "@/lib/site-runtime";

export const dynamic = "force-dynamic";
export const revalidate = 0;

function importModeOf(value: unknown): "replace" | "merge" {
  return value === "merge" ? "merge" : "replace";
}

export async function GET() {
  return adminMethodNotAllowed("POST", "Use POST to import catalog.v1.");
}

export async function POST(request: Request) {
  const blocked = adminWriteBlocked();
  if (blocked) {
    return blocked;
  }

  let raw: unknown;
  try {
    raw = await request.json();
  } catch {
    return adminFail("Import body must be catalog.v1 JSON.");
  }

  const wrapped =
    typeof raw === "object" && raw !== null && "catalog" in raw
      ? (raw as { catalog: unknown; mode?: unknown })
      : null;
  const documentRaw = wrapped ? wrapped.catalog : raw;
  const mode = importModeOf(wrapped?.mode);

  try {
    const catalog =
      typeof documentRaw === "string" ? (JSON.parse(documentRaw) as unknown) : documentRaw;
    const live = await getCatalogDocumentUncached();
    const parsed = parseHandoffCatalog(catalog);
    const incoming = asCatalogDocument(parsed.products, parsed.settings, siteId());
    const next = applyCatalogHandoff(
      live,
      incoming,
      mode,
      settingsForHandoffImport(catalog, live.settings, incoming.settings),
    );
    assertImportSellContract(next.products);
    assertCanonicalSerializedCatalog(toCatalogDocumentJson(next));
    const receipt = await commitCatalogDocument(
      next,
      next.products.map((product) => product.ma),
    );
    return adminReceiptResponse(receipt, { count: receipt.products.length });
  } catch (error) {
    return adminFail(error instanceof Error ? error.message : "Import failed");
  }
}
