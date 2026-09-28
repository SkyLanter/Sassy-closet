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
          <div key={index} aria-hidden>
            <div className="sc-card-well ky-gallery-shell relative aspect-[3/4] overflow-hidden bg-[#f3f1ee]">
              <div className="shimmer pointer-events-none absolute inset-0" />
              <span className="liquid-glass-rim pointer-events-none absolute inset-0 z-[2]" />
              <span className="pointer-events-none absolute inset-x-0 bottom-0 z-[2] h-px bg-gold/45" />
            </div>
            <div className="mt-2.5 h-3 w-10 rounded-sm bg-gold/25" />
            <div className="mt-2 h-5 w-4/5 rounded-sm bg-ink/10" />
            <div className="mt-2 h-3 w-full rounded-sm bg-ink/5" />
            <div className="mt-3 h-3 w-12 rounded-sm bg-ink/10" />
          </div>
        ))}
      </div>
    </div>
  );
}
