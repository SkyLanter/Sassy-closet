import { ShopCatalogDesk } from "@/components/ShopCatalogDesk";
import { loadShopCatalogForAdmin } from "@/lib/shop-catalog-store";

export const dynamic = "force-dynamic";

export default async function ShopToolsPage() {
  const initial = await loadShopCatalogForAdmin();
  return <ShopCatalogDesk initial={initial} />;
}
