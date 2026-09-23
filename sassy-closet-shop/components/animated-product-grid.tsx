"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ProductGrid } from "@/components/product-grid";
import { FILTER_POUR_SECONDS, filterSlide } from "@/lib/motion";
import type { ShopLook } from "@/lib/shop-look";

export function AnimatedProductGrid({
  products,
  motionKey,
  direction = 1,
}: {
  products: ShopLook[];
  motionKey: string;
  direction?: number;
}) {
  const reduced = useReducedMotion();
  const slide = filterSlide(Boolean(reduced), direction);

  return (
    <div className="featured-pour-stack">
      <AnimatePresence mode="sync" initial={false}>
        <motion.div
          key={motionKey}
          data-filter-ms={String(Math.round(FILTER_POUR_SECONDS * 1000))}
          data-filter-slide=""
          className="featured-pour featured-pour-layer"
          initial={slide.initial}
          animate={slide.animate}
          exit={slide.exit}
        >
          <ProductGrid products={products} replay={false} />
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
