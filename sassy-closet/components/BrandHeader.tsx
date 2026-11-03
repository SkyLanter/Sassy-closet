export function BrandHeader() {
  return (
    <header data-testid="brand-mark" className="min-w-0 text-left">
      <p
        data-testid="intake-kicker"
        className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#a85d74]"
      >
        Intake · Nhận đồ
      </p>
      <h1
        data-testid="site-title"
        className="font-script mt-1 text-[2.35rem] font-normal leading-none text-[#5c3d48] sm:text-[2.75rem]"
      >
        Sassy Closet
      </h1>
      <p className="mt-1 max-w-md text-[13.5px] leading-snug text-[#7d5360]">
        Ảnh, size, màu, link shop. Lưu để lấy mã.
      </p>
    </header>
  );
}
