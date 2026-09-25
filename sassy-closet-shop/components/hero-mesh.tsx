import Link from "next/link";

/**
 * Live hero: D02 front + back diptych with a soft overlay —
 * value prop + CTAs. No mã letter on the overlay.
 */
export function HeroEditorial() {
  return (
    <section className="hero-editorial relative isolate overflow-hidden bg-blush">
      <Link
        href="/m/D02"
        aria-label="Đầm trắng WITHMIN · White WITHMIN dress — xem chi tiết · view details"
        className="group relative block touch-manipulation"
      >
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-px bg-ink/10">
          {/* Front */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/products/D02/photo-4.jpg"
            alt=""
            draggable={false}
            decoding="async"
            fetchPriority="high"
            width={900}
            height={1200}
            className="aspect-[3/4] h-auto w-full select-none object-cover object-center motion-safe:transition-opacity motion-safe:duration-300 group-hover:opacity-[0.97]"
            sizes="(max-width: 768px) 50vw, 640px"
          />
          {/* Back */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/products/D02/photo-2.jpg"
            alt=""
            draggable={false}
            decoding="async"
            fetchPriority="high"
            width={900}
            height={1200}
            className="aspect-[3/4] h-auto w-full select-none object-cover object-center motion-safe:transition-opacity motion-safe:duration-300 group-hover:opacity-[0.97]"
            sizes="(max-width: 768px) 50vw, 640px"
          />
        </div>
      </Link>
      {/* Legibility scrim for the overlay copy — clicks pass through to the look link. */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-gradient-to-t from-ink/65 via-ink/15 to-transparent"
      />
      {/* Value prop + CTAs. Copy block is pointer-transparent; only the CTAs take taps. */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0">
        <div className="mx-auto max-w-7xl px-5 pb-5 text-center sm:px-8 sm:pb-9">
          <p
            className="text-[10px] font-medium uppercase tracking-[0.22em] text-paper/85 sm:text-[11px]"
            translate="no"
          >
            Hàng mới về · New in
          </p>
          <h1
            className="mt-1.5 font-display text-[1.7rem] font-medium leading-[1.1] tracking-[0.02em] text-paper sm:mt-2 sm:text-5xl"
            translate="no"
          >
            Đồ xinh cho nàng
          </h1>
          <p
            className="mt-1.5 hidden text-[13px] leading-relaxed text-paper/90 sm:block"
            translate="no"
          >
            Nhắn tin là mua được · Just message to buy
          </p>
          <div className="pointer-events-auto mt-3 flex flex-wrap items-center justify-center gap-2 sm:mt-5 sm:gap-3">
            <Link
              href="/m/D02"
              aria-label="Xem Đầm trắng WITHMIN · View the White WITHMIN dress"
              className="inline-flex min-h-11 touch-manipulation items-center justify-center rounded-full bg-paper px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-ink sm:px-6 sm:text-[11px]"
            >
              Xem ngay · Shop the look
            </Link>
            <Link
              href="#looks-heading"
              className="inline-flex min-h-11 touch-manipulation items-center justify-center rounded-full border border-paper/70 px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-paper sm:px-6 sm:text-[11px]"
            >
              Tất cả looks · All looks
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
