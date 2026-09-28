import { redirect } from "next/navigation";
import { ShopCatalogDesk } from "@/components/ShopCatalogDesk";
import { hasShopAdminSession } from "@/lib/admin-session";
import { loadShopCatalogForAdmin } from "@/lib/shop-catalog-store";

export const dynamic = "force-dynamic";

export default async function ShopToolsPage() {
  if (!(await hasShopAdminSession())) {
    redirect("/admin/shop/login");
  }
  const initial = await loadShopCatalogForAdmin();
  return <ShopCatalogDesk initial={initial} />;
}
