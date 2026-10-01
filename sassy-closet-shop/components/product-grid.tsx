"use client";

import { motion, useReducedMotion } from "framer-motion";
import { ProductCard } from "@/components/product-card";
import { ShopEmpty } from "@/components/shop-empty";
import { LOOK_GRID_SIZES, RELATED_LOOK_SIZES } from "@/lib/look-card-photo";
import { staggerContainer } from "@/lib/motion";
import type { ShopLook } from "@/lib/shop-look";

export function ProductGrid({
  products,
  replay = false,
  namedCovers = true,
  eagerCount = 2,
  variant = "full",
}: {
  products: ShopLook[];
  replay?: boolean;
  namedCovers?: boolean;
  eagerCount?: number;
  variant?: "full" | "compact";
}) {
  const reduced = useReducedMotion();
  const sizes = variant === "compact" ? RELATED_LOOK_SIZES : LOOK_GRID_SIZES;

  if (products.length === 0) {
    return (
      <ShopEmpty
        title="This collection"
        body="Chưa có look trên lookbook · Nothing listed here yet."
      />
    );
  }

  return (
    <motion.ul
      className="sc-look-grid grid min-w-0 gap-x-3 gap-y-12 sm:gap-x-5"
      variants={replay ? staggerContainer(Boolean(reduced)) : undefined}
      initial={replay && !reduced ? "hidden" : false}
      animate={replay ? "show" : undefined}
    >
      {products.map((product, index) => (
        <ProductCard
          key={product.ma}
          product={product}
          priority={index < eagerCount}
          namedCover={namedCovers}
          variant={variant}
          sizes={sizes}
        />
      ))}
    </motion.ul>
  );
}
