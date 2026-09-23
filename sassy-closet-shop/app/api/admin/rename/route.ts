import { mergeItemFieldsFromBody } from "@/lib/admin-json-body";
import { fieldsFromProduct, renameProductInCatalog } from "@/lib/admin-ops";
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

type RenameBody = {
  from?: unknown;
  to?: unknown;
};

export async function GET() {
  return adminMethodNotAllowed("POST", "Use POST to change mã.");
}

export async function POST(request: Request) {
  const blocked = adminWriteBlocked();
  if (blocked) {
    return blocked;
  }

  let body: RenameBody;
  try {
    body = (await request.json()) as RenameBody;
  } catch {
    return adminFail("Change mã body must be JSON.");
  }

  const from = typeof body.from === "string" ? normalizeMa(body.from) : "";
  const to = typeof body.to === "string" ? normalizeMa(body.to) : "";
  if (!from || !to) {
    return adminFail("Change mã needs from and to.");
  }
  if (!isSellableMa(from) || !isSellableMa(to)) {
    return adminFail(nonAllowlistSaveError(isSellableMa(to) ? from : to));
  }

  const document = await readLiveCatalogDocument();
  const current = document.products.find((product) => product.ma === from);
  if (!current) {
    return adminFail(`Mã ${from} is not in the catalog`);
  }

  const result = renameProductInCatalog(
    document.products,
    from,
    to,
    mergeItemFieldsFromBody(body, fieldsFromProduct(current)),
  );
  if (!result.ok) {
    return adminFail(result.error);
  }

  try {
    const receipt = await commitProductList(result.products, [from, result.ma], {
      ma: result.ma,
      renamedTo: result.ma,
    });
    return adminReceiptResponse(receipt);
  } catch (error) {
    return adminFail(error instanceof Error ? error.message : "Change mã failed", 500);
  }
}
