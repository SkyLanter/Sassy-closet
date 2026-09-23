import type { Metadata } from "next";
import { AdminConsole } from "@/app/admin/console";
import { AdminFrame } from "@/app/admin/frame";
import { loadAdminPageData } from "@/app/admin/load";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Site settings · Sell ops",
  robots: { index: false, follow: false },
};

export default async function AdminSettingsPage() {
  const data = await loadAdminPageData();

  return (
    <AdminFrame>
      <AdminConsole
        initialProducts={data.products}
        initialSettings={data.settings}
        storage={data.storage}
        site={data.site}
        pipeline={data.pipeline}
        mode="settings"
      />
    </AdminFrame>
  );
}
