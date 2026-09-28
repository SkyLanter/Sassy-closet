export default function ProductLoading() {
  return (
    <div
      className="mx-auto grid max-w-7xl gap-8 ky-gutter py-8 lg:grid-cols-2 lg:gap-14 lg:py-12"
      role="status"
      aria-busy="true"
      aria-live="polite"
    >
      <div className="sc-card-well relative aspect-[3/4] overflow-hidden bg-[#f3f1ee]" aria-hidden>
        <div className="shimmer pointer-events-none absolute inset-0" />
      </div>
      <div aria-hidden>
        <div className="h-3 w-24 rounded-sm bg-gold/30" />
        <div className="mt-4 h-3 w-16 rounded-sm bg-gold/25" />
        <div className="mt-3 h-10 w-4/5 max-w-sm rounded-sm bg-ink/10" />
        <div className="mt-4 h-5 w-16 rounded-sm bg-ink/10" />
        <div className="mt-6 h-3 w-full max-w-md rounded-sm bg-ink/5" />
        <div className="mt-2 h-3 w-2/3 max-w-sm rounded-sm bg-ink/5" />
        <p className="mt-8 text-[11px] uppercase tracking-[0.16em] text-muted" translate="no">
          Đang tải · Loading
        </p>
      </div>
    </div>
  );
}
