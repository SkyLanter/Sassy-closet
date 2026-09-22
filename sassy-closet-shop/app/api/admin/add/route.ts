import { addProductToCatalog, type ProductFieldsInput } from "@/lib/admin-ops";
import { isAddLetter, mergeAddFields } from "@/lib/admin-add";
import {
  adminFail,
  adminMethodNotAllowed,
  adminReceiptResponse,
  adminWriteBlocked,
} from "@/lib/admin-json-response";
import { getProductsUncached } from "@/lib/products";
import { commitProductList } from "@/lib/save-commit";

export const dynamic = "force-dynamic";
export const revalidate = 0;

type AddBody = {
  letter?: unknown;
} & Partial<ProductFieldsInput>;

export async function GET() {
  return adminMethodNotAllowed(
    "POST",
    "Use POST to Add the next unused mã (A03+). Save writes Blob.",
  );
}

export async function POST(request: Request) {
  const blocked = adminWriteBlocked();
  if (blocked) {
    return blocked;
  }

  let body: AddBody;
  try {
    body = (await request.json()) as AddBody;
  } catch {
    return adminFail('Add body must be JSON ({ letter: "A" }).');
  }

  const letterRaw = typeof body.letter === "string" ? body.letter.trim().toUpperCase() : "";
  if (!isAddLetter(letterRaw)) {
    return adminFail(
      "Pick a valid letter (A/Q/V/K/G/P/S/O/H/J/B/D). The mã is assigned on Save.",
    );
  }

  const catalog = await getProductsUncached();
  const fields = mergeAddFields(letterRaw, {
    titleEn: typeof body.titleEn === "string" ? body.titleEn : undefined,
    titleVn: typeof body.titleVn === "string" ? body.titleVn : undefined,
    descriptionEn: typeof body.descriptionEn === "string" ? body.descriptionEn : undefined,
    descriptionVn: typeof body.descriptionVn === "string" ? body.descriptionVn : undefined,
    status: typeof body.status === "string" ? body.status : undefined,
    priceUsd: body.priceUsd === null || typeof body.priceUsd === "number" ? body.priceUsd : undefined,
    colors: body.colors,
    images: body.images,
    sizes: body.sizes,
    fitCm: body.fitCm,
    fulfillment: body.fulfillment,
    sourceLink: body.sourceLink,
  });
  const result = addProductToCatalog(catalog, letterRaw, fields);
  if (!result.ok) {
    return adminFail(result.error);
  }

  try {
    const receipt = await commitProductList(result.products, [result.ma], {
      ma: result.ma,
      nextMa: result.ma,
    });
    return adminReceiptResponse(receipt);
  } catch (error) {
    return adminFail(error instanceof Error ? error.message : "Add failed", 500);
  }
}
