import type { Metadata } from "next";
import { AdminConsole } from "@/app/admin/console";
import { AdminFrame } from "@/app/admin/frame";
import { loadAdminPageData } from "@/app/admin/load";
import { normalizeMa } from "@/lib/ma";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Edit item · Sell ops",
  robots: { index: false, follow: false },
};

export default async function AdminEditPage({
  params,
  searchParams,
}: {
  params: Promise<{ ma: string }>;
  searchParams: Promise<{ added?: string; renamedFrom?: string; saved?: string }>;
}) {
  const { ma: rawMa } = await params;
  const query = await searchParams;
  const ma = normalizeMa(rawMa);
  const data = await loadAdminPageData();
  const added = query.added === "1";
  const renamedFrom = query.renamedFrom ? normalizeMa(query.renamedFrom) : "";
  const saved = query.saved === "1";
  const notice = added
    ? `Saved ${ma}. Blob catalog updated.`
    : renamedFrom
      ? `Changed mã ${renamedFrom} → ${ma}. Current fields were saved.`
      : saved
        ? `Saved ${ma}. The shop is reading this catalog.`
        : undefined;

  return (
    <AdminFrame>
      <AdminConsole
        initialProducts={data.products}
        initialSettings={data.settings}
        storage={data.storage}
        site={data.site}
        pipeline={data.pipeline}
        mode="edit"
        editMa={ma}
        notice={notice}
      />
    </AdminFrame>
  );
}
