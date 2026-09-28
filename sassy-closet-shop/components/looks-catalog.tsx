"use client";

import { useMemo, useState } from "react";
import { AnimatedProductGrid } from "@/components/animated-product-grid";
import { ContentWaveLooks } from "@/components/content-wave";
import { LooksSortChips } from "@/components/looks-sort";
import { SearchResultsBar } from "@/components/search-results-bar";
import { CategorySuggestChips } from "@/components/category-suggest-chips";
import { ShopEmpty } from "@/components/shop-empty";
import { SizeFilterChips } from "@/components/size-filter";
import { useShopSearch } from "@/components/shop-search";
import type { AsiaSizeLetter } from "@/lib/asia-size";
import { DEFAULT_SHOP_SORT, sortShopLooks, type ShopSortId } from "@/lib/fb-rank";
import { filterLooksByQuery, LOOK_SEARCH_NO_MATCH, shopSearchNeedle } from "@/lib/look-search";
import { collectShopSizes } from "@/lib/shop-sizes";
import type { MaLetter } from "@/lib/ma";
import type { ShopLook } from "@/lib/shop-look";

export function LooksCatalog({
  products,
  motionKey,
  suggestTypes = [],
}: {
  products: ShopLook[];
  motionKey: string;
  suggestTypes?: MaLetter[];
}) {
  const [sort, setSort] = useState<ShopSortId>(DEFAULT_SHOP_SORT);
  const [size, setSize] = useState<AsiaSizeLetter | null>(null);
  const { draft, clearSearch } = useShopSearch();
  const needle = shopSearchNeedle(draft, "");
  const searched = useMemo(() => filterLooksByQuery(products, needle), [needle, products]);
  const sizeOptions = useMemo(() => collectShopSizes(searched), [searched]);
  const activeSize = size && sizeOptions.includes(size) ? size : null;
  const visible = useMemo(() => {
    const filtered = activeSize
      ? searched.filter((product) => product.sizes.includes(activeSize))
      : searched;
    return sortShopLooks(filtered, sort);
  }, [activeSize, searched, sort]);

  return (
    <div data-shop-sort={sort} data-shop-size={activeSize ?? undefined} data-shop-search={needle || undefined}>
      <LooksSortChips sort={sort} onChange={setSort} />
      <SizeFilterChips sizes={sizeOptions} selected={activeSize} onChange={setSize} />
      <SearchResultsBar query={needle} count={visible.length} />
      <div className="mt-8 overflow-hidden">
        <ContentWaveLooks>
          {visible.length === 0 ? (
            <ShopEmpty
              title="Looks"
              body={
                needle.trim()
                  ? LOOK_SEARCH_NO_MATCH
                  : activeSize
                    ? `Không có size ${activeSize} · No size ${activeSize} in this view.`
                    : "Chưa có looks trên lookbook · No looks listed."
              }
              actions={
                needle.trim() || activeSize ? (
                  <div className="mt-5 px-2">
                    <div className="flex flex-wrap items-center justify-center gap-2">
                      {needle.trim() ? (
                        <button
                          type="button"
                          className="inline-flex min-h-11 touch-manipulation items-center rounded-full border border-gold/45 px-4 text-[13px] text-ink"
                          onClick={() => clearSearch()}
                        >
                          Xóa tìm · Clear search
                        </button>
                      ) : null}
                      {activeSize ? (
                        <button
                          type="button"
                          className="inline-flex min-h-11 touch-manipulation items-center rounded-full border border-gold/45 px-4 text-[13px] text-ink"
                          onClick={() => setSize(null)}
                        >
                          Xóa size · Clear size
                        </button>
                      ) : null}
                    </div>
                    {needle.trim() && searched.length === 0 ? (
                      <CategorySuggestChips types={suggestTypes} className="mt-5" />
                    ) : null}
                  </div>
                ) : null
              }
            />
          ) : (
            <AnimatedProductGrid products={visible} motionKey={`${motionKey}-${sort}-${needle}`} />
          )}
        </ContentWaveLooks>
      </div>
    </div>
  );
}
