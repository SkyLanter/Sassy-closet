import { mergeItemFieldsFromBody } from "@/lib/admin-json-body";
import { fieldsFromProduct, saveProductInCatalog } from "@/lib/admin-ops";
import {
  adminFail,
  adminMethodNotAllowed,
  adminReceiptResponse,
  adminWriteBlocked,
} from "@/lib/admin-json-response";
import { readLiveCatalogDocument } from "@/lib/catalog-store";
import { normalizeMa } from "@/lib/ma";
import { commitProductList } from "@/lib/save-commit";
import { isSellableMa, nonAllowlistSaveError } from "@/lib/sell-contract";

export const dynamic = "force-dynamic";
export const revalidate = 0;

type SaveBody = {
  ma?: unknown;
};

export async function GET() {
  return adminMethodNotAllowed("POST", "Use POST to save a catalog mã.");
}

export async function POST(request: Request) {
  const blocked = adminWriteBlocked();
  if (blocked) {
    return blocked;
  }

  let body: SaveBody;
  try {
    body = (await request.json()) as SaveBody;
  } catch {
    return adminFail("Save body must be JSON.");
  }

  const ma = typeof body.ma === "string" ? normalizeMa(body.ma) : "";
  if (!ma) {
    return adminFail("Save needs a mã.");
  }
  if (!isSellableMa(ma)) {
    return adminFail(nonAllowlistSaveError(ma));
  }

  const document = await readLiveCatalogDocument();
  const current = document.products.find((product) => product.ma === ma);
  if (!current) {
    return adminFail(`Mã ${ma} is not in the catalog`);
  }

  const result = saveProductInCatalog(
    document.products,
    ma,
    mergeItemFieldsFromBody(body, fieldsFromProduct(current)),
  );
  if (!result.ok) {
    return adminFail(result.error);
  }

  try {
    const receipt = await commitProductList(result.products, [result.ma], { ma: result.ma });
    return adminReceiptResponse(receipt);
  } catch (error) {
    return adminFail(error instanceof Error ? error.message : "Save failed", 500);
  }
}
