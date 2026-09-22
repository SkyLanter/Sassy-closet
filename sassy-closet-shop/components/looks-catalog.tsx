"use client";

import { useMemo, useState } from "react";
import { AnimatedProductGrid } from "@/components/animated-product-grid";
import { ContentWaveLooks } from "@/components/content-wave";
import { LooksSortChips } from "@/components/looks-sort";
import { ShopEmpty } from "@/components/shop-empty";
import { useShopSearch } from "@/components/shop-search";
import { DEFAULT_SHOP_SORT, sortShopLooks, type ShopSortId } from "@/lib/fb-rank";
import { filterLooksByQuery, LOOK_SEARCH_NO_MATCH } from "@/lib/look-search";
import type { ShopLook } from "@/lib/shop-look";

export function LooksCatalog({
  products,
  motionKey,
}: {
  products: ShopLook[];
  motionKey: string;
}) {
  const [sort, setSort] = useState<ShopSortId>(DEFAULT_SHOP_SORT);
  const { draft } = useShopSearch();
  const needle = (draft ?? "").trim();
  const visible = useMemo(
    () => sortShopLooks(filterLooksByQuery(products, needle), sort),
    [needle, products, sort],
  );

  return (
    <div data-shop-sort={sort} data-shop-search={needle || undefined}>
      <LooksSortChips sort={sort} onChange={setSort} />
      <div className="mt-8 overflow-hidden">
        <ContentWaveLooks>
          {visible.length === 0 ? (
            <ShopEmpty title="Looks" body={LOOK_SEARCH_NO_MATCH} />
          ) : (
            <AnimatedProductGrid products={visible} motionKey={`${motionKey}-${sort}-${needle}`} />
          )}
        </ContentWaveLooks>
      </div>
    </div>
  );
}
