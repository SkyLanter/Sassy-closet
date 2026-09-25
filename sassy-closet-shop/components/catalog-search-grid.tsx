"use client";

import { useId, useMemo, useState } from "react";
import { AnimatedProductGrid } from "@/components/animated-product-grid";
import { ShopEmpty } from "@/components/shop-empty";
import { filterLooksByQuery } from "@/lib/look-search";
import { lookCountLabel } from "@/lib/look-count";
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
  const inputId = useId();
  const searching = query.trim().length > 0;
  const visible = useMemo(
    () => filterLooksByQuery(products, query),
    [products, query],
  );

  function clear() {
    setQuery("");
  }

  return (
    <div>
      <div className="relative mx-auto mb-8 max-w-md">
        <label className="sr-only" htmlFor={inputId}>
          Tìm mã hoặc tên · Search mã or name
        </label>
        <input
          id={inputId}
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Escape" && query) {
              event.stopPropagation();
              clear();
            }
          }}
          placeholder="Tìm mã hoặc tên… · Search mã or name…"
          className="w-full rounded-full border border-ink/10 bg-paper py-2.5 pl-4 pr-12 text-sm text-ink outline-none ring-ink/20 placeholder:text-muted focus:ring-2"
          autoComplete="off"
          spellCheck={false}
        />
        {query ? (
          <button
            type="button"
            onClick={clear}
            aria-label="Xóa tìm kiếm · Clear search"
            className="absolute right-0 top-1/2 inline-flex min-h-11 min-w-11 -translate-y-1/2 touch-manipulation select-none items-center justify-center rounded-full text-lg leading-none text-muted hover-hover:hover:text-ink"
          >
            <span aria-hidden>×</span>
          </button>
        ) : null}
      </div>
      {searching ? (
        <p
          className="mx-auto mb-6 max-w-md text-center text-[11px] uppercase tracking-[0.16em] text-muted tabular-nums"
          aria-live="polite"
          translate="no"
        >
          {lookCountLabel(visible.length)}
        </p>
      ) : null}
      {visible.length === 0 ? (
        <ShopEmpty title={emptyTitle} body={emptyBody} />
      ) : (
        <AnimatedProductGrid products={visible} motionKey={`${motionKey}:${query}`} />
      )}
    </div>
  );
}
