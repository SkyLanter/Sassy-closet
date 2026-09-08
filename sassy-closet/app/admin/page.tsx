export default function AdminPage() {
  return (
    <main className="mx-auto max-w-md px-4 py-10 text-rose-800">
      <h1 className="text-2xl font-bold">Kit export CSV</h1>
      <p className="mt-2 text-sm text-rose-700/80">
        Chỉ món đã bấm <strong>Lưu & lấy mã</strong>. Không Post, không Square Save.
      </p>
      <a
        className="mt-6 inline-flex h-12 items-center rounded-full bg-primary px-5 font-bold text-primary-foreground"
        href="/api/export"
      >
        Tải CSV
      </a>
    </main>
  );
}
