import { removeProductFromCatalog } from "@/lib/admin-ops";
import {
  adminFail,
  adminMethodNotAllowed,
  adminReceiptResponse,
  adminWriteBlocked,
} from "@/lib/admin-json-response";
import { getProductsUncached } from "@/lib/products";
import { normalizeMa } from "@/lib/ma";
import { commitProductList } from "@/lib/save-commit";

export const dynamic = "force-dynamic";
export const revalidate = 0;

type RemoveBody = {
  ma?: unknown;
};

export async function GET() {
  return adminMethodNotAllowed("POST", "Use POST to remove a catalog mã.");
}

export async function POST(request: Request) {
  const blocked = adminWriteBlocked();
  if (blocked) {
    return blocked;
  }

  let body: RemoveBody;
  try {
    body = (await request.json()) as RemoveBody;
  } catch {
    return adminFail("Remove body must be JSON ({ ma }).");
  }

  const ma = typeof body.ma === "string" ? normalizeMa(body.ma) : "";
  if (!ma) {
    return adminFail("Remove needs a mã.");
  }

  const catalog = await getProductsUncached();
  const result = removeProductFromCatalog(catalog, ma);
  if (!result.ok) {
    return adminFail(result.error);
  }

  try {
    const receipt = await commitProductList(result.products, [result.ma], { ma: result.ma });
    return adminReceiptResponse(receipt);
  } catch (error) {
    return adminFail(error instanceof Error ? error.message : "Remove failed", 500);
  }
}
