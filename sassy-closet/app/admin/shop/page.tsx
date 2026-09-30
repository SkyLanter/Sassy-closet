import { redirect } from "next/navigation";
import { ShopCatalogDesk } from "@/components/ShopCatalogDesk";
import { hasShopAdminSession } from "@/lib/admin-session";
import { loadShopDatasetRows } from "@/lib/shop-dataset-read";
import { loadShopCatalogForAdmin } from "@/lib/shop-catalog-store";
import { listSubmissions } from "@/lib/store";

export const dynamic = "force-dynamic";

export default async function ShopToolsPage() {
  if (!(await hasShopAdminSession())) {
    redirect("/admin/shop/login");
  }
  const [initial, submissions, shopRows] = await Promise.all([
    loadShopCatalogForAdmin(),
    listSubmissions().catch(() => []),
    loadShopDatasetRows(),
  ]);
  return (
    <ShopCatalogDesk initial={initial} intakeMas={submissions.map((row) => row.ma)} shopRows={shopRows} />
  );
}
