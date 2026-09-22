import type { Metadata } from "next";
import { AdminConsole } from "@/app/admin/console";
import { AdminFrame } from "@/app/admin/frame";
import { loadAdminPageData } from "@/app/admin/load";
import { normalizeMa } from "@/lib/ma";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Sell ops",
  robots: { index: false, follow: false },
};

export default async function AdminPage({
  searchParams,
}: {
  searchParams: Promise<{ removed?: string }>;
}) {
  const data = await loadAdminPageData();
  const query = await searchParams;
  const removed = query.removed ? normalizeMa(query.removed) : "";

  return (
    <AdminFrame>
      <AdminConsole
        initialProducts={data.products}
        initialSettings={data.settings}
        storage={data.storage}
        site={data.site}
        mode="list"
        notice={removed ? `Removed ${removed} from the catalog. It is gone from the shop.` : undefined}
      />
    </AdminFrame>
  );
}
