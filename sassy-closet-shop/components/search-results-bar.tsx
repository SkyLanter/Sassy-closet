"use client";

import { useShopSearch } from "@/components/shop-search";

export function SearchResultsBar({ query }: { query: string }) {
  const { clearSearch } = useShopSearch();
  const shown = query.trim().slice(0, 40);
  if (!shown) {
    return null;
  }

  return (
    <div
      data-testid="shop-search-results"
      className="mt-4 flex min-w-0 flex-wrap items-center justify-between gap-x-3 gap-y-1 rounded-2xl border border-gold/40 bg-blush/40 px-3 py-2"
    >
      <p className="min-w-0 break-words text-[13px] leading-snug text-ink" translate="no">
        Đang hiện “{shown}” · Showing results for “{shown}”
      </p>
      <button
        type="button"
        data-testid="shop-search-results-clear"
        className="inline-flex min-h-11 shrink-0 touch-manipulation items-center rounded-full border border-gold/45 px-4 text-[13px] text-ink"
        onClick={() => clearSearch()}
      >
        Xóa · Clear
      </button>
    </div>
  );
}
