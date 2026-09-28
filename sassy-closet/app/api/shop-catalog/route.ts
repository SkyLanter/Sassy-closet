import { requireShopAdmin, shopAdminJson } from "@/lib/shop-admin-http";
import { listShopCatalog } from "@/lib/shop-catalog";
import { shopCatalogPortFromEnv } from "@/lib/shop-catalog-store";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const denied = await requireShopAdmin(request);
  if (denied) {
    return denied;
  }
  const selected = shopCatalogPortFromEnv();
  if (!selected.ok) {
    return shopAdminJson({ ok: false, error: selected.error }, 503);
  }
  const document = await selected.port.read();
  if (document === null) {
    return shopAdminJson({ ok: false, error: "Shop catalog is missing." }, 404);
  }
  const listed = listShopCatalog(document);
  if (!listed.ok) {
    return shopAdminJson({ ok: false, error: listed.error }, 500);
  }
  return shopAdminJson(listed);
}
