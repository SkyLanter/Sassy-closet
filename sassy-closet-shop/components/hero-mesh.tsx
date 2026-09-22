import Link from "next/link";

/** Live hero: D02 front + back diptych only — no mã letter on the overlay. */
export function HeroEditorial() {
  return (
    <section className="hero-editorial relative isolate overflow-hidden bg-blush">
      <Link
        href="/m/D02"
        aria-label="Sassy Closet · Đầm trắng WITHMIN · White WITHMIN dress"
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
    </section>
  );
}
