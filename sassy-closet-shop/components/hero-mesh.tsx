import Image from "next/image";
import Link from "next/link";
import { BLUSH_BLUR } from "@/lib/image-placeholder";

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
          <Image
            src="/products/D02/photo-4.jpg"
            alt=""
            draggable={false}
            priority
            width={900}
            height={1200}
            placeholder="blur"
            blurDataURL={BLUSH_BLUR}
            className="aspect-[3/4] h-auto w-full select-none object-cover object-center motion-safe:transition-opacity motion-safe:duration-150 group-hover:opacity-[0.97]"
            sizes="(max-width: 768px) 50vw, 640px"
          />
          <Image
            src="/products/D02/photo-2.jpg"
            alt=""
            draggable={false}
            priority
            width={900}
            height={1200}
            placeholder="blur"
            blurDataURL={BLUSH_BLUR}
            className="aspect-[3/4] h-auto w-full select-none object-cover object-center motion-safe:transition-opacity motion-safe:duration-150 group-hover:opacity-[0.97]"
            sizes="(max-width: 768px) 50vw, 640px"
          />
        </div>
      </Link>
    </section>
  );
}
