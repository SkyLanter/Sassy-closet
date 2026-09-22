export default function ShopLoading() {
  return (
    <div className="mx-auto max-w-7xl ky-gutter py-10 sm:py-12" role="status" aria-busy="true" aria-live="polite" aria-atomic="true">
      <p className="text-left font-display text-[2.15rem] font-medium leading-[1.08] tracking-[0.02em] text-balance text-ink outline-none sm:text-[2.75rem]" translate="no">
        Looks
      </p>
      <p className="liquid-glass-chip mx-auto mt-3 flex min-h-11 w-max max-w-full select-none items-center justify-center truncate whitespace-nowrap px-3 py-1.5 text-center text-[11px] uppercase tracking-[0.18em] text-muted" translate="no">
        Đang tải · Loading
      </p>
      <div className="mt-10 grid min-w-0 grid-cols-2 gap-x-3 gap-y-12 sm:grid-cols-3 sm:gap-x-5 lg:grid-cols-4 xl:grid-cols-5">
        {Array.from({ length: 8 }, (_, index) => (
          <div key={index} className="ky-gallery-shell relative aspect-[3/4] overflow-hidden bg-[#f3f1ee]" aria-hidden>
            <div className="shimmer pointer-events-none absolute inset-0" aria-hidden />
            <span className="liquid-glass-rim pointer-events-none absolute inset-0 z-[2]" aria-hidden />
            <span className="pointer-events-none absolute inset-x-0 bottom-0 z-[2] h-px origin-center scale-x-100 bg-gold/45" aria-hidden />
          </div>
        ))}
      </div>
    </div>
  );
}
