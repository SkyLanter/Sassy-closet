import { storeHealth } from "@/lib/store";

export const dynamic = "force-dynamic";

export default async function AdminPage() {
  const storage = storeHealth();
  return (
    <main className="mx-auto max-w-md px-4 py-10 text-[#5c3d48]">
      <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#a85d74]">Intake</p>
      <h1 className="mt-1 text-[21px] font-semibold text-[#3c2a2e]">Kit export CSV</h1>
      <p className="mt-2 text-[13.5px] leading-relaxed text-[#7d5360]">
        Chỉ món đã bấm <strong>Lưu & lấy mã</strong>. Không Post, không Square Save.
      </p>
      <p
        data-testid="storage-mode"
        className={`mt-4 text-sm ${storage.durable ? "text-rose-700/80" : "font-semibold text-rose-800"}`}
      >
        Kho: {storage.durable ? "durable (Vercel Blob)" : storage.mode === "ephemeral" ? "tạm /tmp — redeploy sẽ mất" : "máy local (data/)"}
        {storage.warning ? ` · ${storage.warning}` : ""}
      </p>
      <a
        className="mt-6 inline-flex h-12 items-center rounded-full bg-primary px-5 font-bold text-primary-foreground"
        href="/api/export"
      >
        Tải CSV
      </a>
      <p className="mt-6 text-sm">
        <a className="underline-offset-2 hover:underline" href="/admin/shop">
          Shop tools
        </a>
      </p>
      <p className="mt-2 text-xs text-[#7d5360]">Trang riêng, có mật khẩu. Không nằm trong form nhận đồ.</p>
    </main>
  );
}
