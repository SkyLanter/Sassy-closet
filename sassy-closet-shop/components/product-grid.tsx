"use client";

import { motion, useReducedMotion } from "framer-motion";
import { ProductCard } from "@/components/product-card";
import { ShopEmpty } from "@/components/shop-empty";
import { staggerContainer } from "@/lib/motion";
import type { ShopLook } from "@/lib/shop-look";

export function ProductGrid({
  products,
  replay = false,
  namedCovers = true,
}: {
  products: ShopLook[];
  replay?: boolean;
  namedCovers?: boolean;
}) {
  const reduced = useReducedMotion();

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
      className="grid min-w-0 grid-cols-2 gap-x-3 gap-y-10 sm:grid-cols-3 sm:gap-x-4 lg:grid-cols-4 xl:grid-cols-5"
      variants={replay ? staggerContainer(Boolean(reduced)) : undefined}
      initial={replay && !reduced ? "hidden" : false}
      animate={replay ? "show" : undefined}
    >
      {products.map((product, index) => (
        <ProductCard
          key={product.ma}
          product={product}
          priority={index < 4}
          namedCover={namedCovers}
        />
      ))}
    </motion.ul>
  );
}
