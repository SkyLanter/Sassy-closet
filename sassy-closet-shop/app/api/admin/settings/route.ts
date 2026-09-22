import { asCatalogDocument } from "@/lib/product-parse";
import {
  adminFail,
  adminMethodNotAllowed,
  adminReceiptResponse,
  adminWriteBlocked,
} from "@/lib/admin-json-response";
import { getCatalogDocumentUncached } from "@/lib/products";
import { commitCatalogDocument } from "@/lib/save-commit";
import { parseSiteSettings } from "@/lib/site-settings";

export const dynamic = "force-dynamic";
export const revalidate = 0;

type SettingsBody = {
  announcementLines?: unknown;
  facebookPageUrl?: unknown;
};

export async function GET() {
  return adminMethodNotAllowed("POST", "Use POST to save site settings.");
}

export async function POST(request: Request) {
  const blocked = adminWriteBlocked();
  if (blocked) {
    return blocked;
  }

  let body: SettingsBody;
  try {
    body = (await request.json()) as SettingsBody;
  } catch {
    return adminFail("Settings body must be JSON.");
  }

  try {
    const document = await getCatalogDocumentUncached();
    const settings = parseSiteSettings({
      announcementLines: Array.isArray(body.announcementLines) ? body.announcementLines : [],
      facebookPageUrl: typeof body.facebookPageUrl === "string" ? body.facebookPageUrl : "",
    });
    const receipt = await commitCatalogDocument(
      asCatalogDocument(document.products, settings, document.siteId),
      document.products.map((product) => product.ma),
    );
    return adminReceiptResponse(receipt);
  } catch (error) {
    return adminFail(error instanceof Error ? error.message : "Settings save failed", 500);
  }
}
