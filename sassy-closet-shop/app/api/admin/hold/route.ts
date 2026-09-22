import { bulkHoldInCatalog } from "@/lib/admin-ops";
import {
  adminFail,
  adminMethodNotAllowed,
  adminReceiptResponse,
  adminWriteBlocked,
} from "@/lib/admin-json-response";
import { getProductsUncached } from "@/lib/products";
import { normalizeMa } from "@/lib/ma";
import { commitProductList } from "@/lib/save-commit";
import { isSellableMa, nonAllowlistSaveError } from "@/lib/sell-contract";

export const dynamic = "force-dynamic";
export const revalidate = 0;

type HoldBody = {
  mas?: unknown;
};

export async function GET() {
  return adminMethodNotAllowed("POST", "Use POST to Hold selected mãs.");
}

export async function POST(request: Request) {
  const blocked = adminWriteBlocked();
  if (blocked) {
    return blocked;
  }

  let body: HoldBody;
  try {
    body = (await request.json()) as HoldBody;
  } catch {
    return adminFail("Hold body must be JSON ({ mas }).");
  }

  const mas = Array.isArray(body.mas)
    ? body.mas
        .map((value) => (typeof value === "string" ? normalizeMa(value) : ""))
        .filter((ma) => ma.length > 0)
    : [];
  if (mas.length === 0) {
    return adminFail("Hold needs at least one mã.");
  }
  for (const ma of mas) {
    if (!isSellableMa(ma)) {
      return adminFail(nonAllowlistSaveError(ma));
    }
  }

  const catalog = await getProductsUncached();
  const result = bulkHoldInCatalog(catalog, mas);
  if (!result.ok) {
    return adminFail(result.error);
  }

  try {
    const receipt = await commitProductList(result.products, mas, { ma: result.ma });
    return adminReceiptResponse(receipt);
  } catch (error) {
    return adminFail(error instanceof Error ? error.message : "Bulk Hold failed", 500);
  }
}
