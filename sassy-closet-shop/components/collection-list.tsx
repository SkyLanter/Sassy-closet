"use client";

import Link from "next/link";
import { useMemo } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { ShopEmpty } from "@/components/shop-empty";
import { categoryAriaLabel, categoryCopy, categoryHref, categoryTileSrc } from "@/lib/categories";
import { fadeUp, staggerContainer } from "@/lib/motion";
import type { MaLetter } from "@/lib/ma";
import type { ShopLook } from "@/lib/shop-look";

function tileForType(type: MaLetter, products: ShopLook[]): string {
  const match = products.find((product) => product.type === type && product.images[0]?.src);
  return match?.images[0]?.src ?? categoryTileSrc(type);
}

export function CollectionList({
  types,
  products = [],
}: {
  types: MaLetter[];
  products?: ShopLook[];
}) {
  const reduced = useReducedMotion();
  const tiles = useMemo(() => {
    const next: Partial<Record<MaLetter, string>> = {};
    for (const type of types) {
      next[type] = tileForType(type, products);
    }
    return next;
  }, [types, products]);

  if (types.length === 0) {
    return (
      <section className="bg-paper ky-gutter py-12">
        <ShopEmpty
          title="Collections"
          body="Chưa có bộ sưu tập trên lookbook · No collections listed."
        />
      </section>
    );
  }

  return (
    <section className="bg-paper">
      <motion.ul
        aria-label="Bộ sưu tập · Collections"
        className="ky-collection-rail flex snap-x snap-mandatory overflow-x-auto tab-scroll md:grid md:grid-cols-3 md:overflow-visible lg:grid-cols-5"
        variants={staggerContainer(Boolean(reduced))}
        initial={false}
        animate="show"
      >
        {types.map((type, index) => {
          const labels = categoryCopy(type);
          const src = tiles[type] ?? categoryTileSrc(type);
          return (
            <motion.li
              key={type}
              variants={fadeUp(Boolean(reduced))}
              aria-posinset={index + 1}
              aria-setsize={types.length}
              className="w-[42%] shrink-0 snap-center snap-always md:w-auto"
            >
              <Link
                href={categoryHref(type)}
                aria-label={categoryAriaLabel(type)}
                className="group relative block aspect-[3/4] overflow-hidden touch-manipulation"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={src}
                  alt=""
                  draggable={false}
                  decoding="async"
                  fetchPriority={index < 2 ? "high" : "auto"}
                  loading={index < 2 ? "eager" : "lazy"}
                  sizes="(max-width: 768px) 42vw, (max-width: 1024px) 33vw, 20vw"
                  className="h-full w-full select-none object-cover motion-safe:transition-transform motion-safe:duration-700 motion-safe:ease-out motion-safe:hover-hover:group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/55 via-ink/5 to-transparent" aria-hidden />
                <span className="pointer-events-none absolute inset-x-0 bottom-0 z-[2] h-px origin-center scale-x-100 bg-gold/45" aria-hidden />
                <span className="pointer-events-none absolute inset-x-0 bottom-5 select-none px-3 text-center text-[10px] font-medium uppercase tracking-[0.16em] text-paper whitespace-nowrap [text-shadow:0_1px_10px_rgba(17,17,17,0.55)]" translate="no" aria-hidden>
                  {labels.label}
                </span>
              </Link>
            </motion.li>
          );
        })}
      </motion.ul>
    </section>
  );
}
