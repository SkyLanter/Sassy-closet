import { shopAdminJson } from "@/lib/shop-admin-http";
import { listShopCatalog, readShopCatalogDocument } from "@/lib/shop-catalog";
import { shopCatalogPortFromEnv } from "@/lib/shop-catalog-store";

export const dynamic = "force-dynamic";

export async function GET() {
  const selected = shopCatalogPortFromEnv();
  if (!selected.ok) {
    return shopAdminJson({ ok: false, error: selected.error }, 503);
  }
  const read = await readShopCatalogDocument(selected.port);
  if (!read.ok) {
    return shopAdminJson({ ok: false, error: read.error }, read.status);
  }
  const listed = listShopCatalog(read.document);
  if (!listed.ok) {
    return shopAdminJson({ ok: false, error: listed.error }, 500);
  }
  return shopAdminJson(listed);
}
