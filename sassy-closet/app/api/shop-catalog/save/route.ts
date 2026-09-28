import { requireShopAdmin, shopAdminJson } from "@/lib/shop-admin-http";
import { saveShopCatalogProduct } from "@/lib/shop-catalog";
import { shopCatalogPortFromEnv } from "@/lib/shop-catalog-store";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const denied = await requireShopAdmin(request);
  if (denied) {
    return denied;
  }
  return shopAdminJson({ ok: false, error: "Use POST to save a catalog mã." }, 405, { Allow: "POST" });
}

export async function POST(request: Request) {
  const denied = await requireShopAdmin(request);
  if (denied) {
    return denied;
  }
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return shopAdminJson({ ok: false, error: "Save body must be JSON." }, 400);
  }
  const selected = shopCatalogPortFromEnv();
  if (!selected.ok) {
    return shopAdminJson({ ok: false, error: selected.error }, 503);
  }
  const result = await saveShopCatalogProduct(selected.port, body);
  if (!result.ok) {
    return shopAdminJson(
      {
        ok: false,
        error: result.error,
        blobWritten: result.blobWritten,
        ma: result.ma,
        updatedAt: result.updatedAt,
      },
      result.status,
    );
  }
  return shopAdminJson({
    ok: true,
    ma: result.ma,
    blobWritten: result.blobWritten,
    revalidated: result.revalidated,
    updatedAt: result.updatedAt,
  });
}
