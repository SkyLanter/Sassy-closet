"use client";

import { useMemo, useState } from "react";
import { AnimatedProductGrid } from "@/components/animated-product-grid";
import { ShopEmpty } from "@/components/shop-empty";
import type { ShopLook } from "@/lib/shop-look";

export function CatalogSearchGrid({
  products,
  motionKey,
  emptyTitle,
  emptyBody,
}: {
  products: ShopLook[];
  motionKey: string;
  emptyTitle: string;
  emptyBody: string;
}) {
  const [query, setQuery] = useState("");
  const visible = useMemo(() => {
    const q = query.trim().toLocaleLowerCase("vi");
    if (!q) {
      return products;
    }
    return products.filter((product) => {
      const hay = `${product.ma} ${product.titleVn} ${product.titleEn}`.toLocaleLowerCase("vi");
      return hay.includes(q);
    });
  }, [products, query]);

  return (
    <div>
      <label className="mx-auto mb-8 block max-w-md">
        <span className="sr-only">Tìm mã hoặc tên · Search mã or name</span>
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Tìm mã hoặc tên… · Search mã or name…"
          className="w-full rounded-full border border-ink/10 bg-paper px-4 py-2.5 text-sm text-ink outline-none ring-ink/20 placeholder:text-muted focus:ring-2"
          autoComplete="off"
          spellCheck={false}
        />
      </label>
      {visible.length === 0 ? (
        <ShopEmpty title={emptyTitle} body={emptyBody} />
      ) : (
        <AnimatedProductGrid products={visible} motionKey={`${motionKey}:${query}`} />
      )}
    </div>
  );
}
