"use client";

import { Suspense, useCallback, useId, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { AnimatedProductGrid } from "@/components/animated-product-grid";
import { ContentWaveLooks } from "@/components/content-wave";
import { LooksSortChips } from "@/components/looks-sort";
import { ShopEmpty } from "@/components/shop-empty";
import { useShopSearch } from "@/components/shop-search";
import {
  ASIA_SIZE_LETTERS,
  isAsiaSizeLetter,
  type AsiaSizeLetter,
} from "@/lib/asia-size";
import { HOLD_ASK_LABEL, HOLD_PRICE_LABEL } from "@/lib/dropship-copy";
import { DEFAULT_SHOP_SORT, sortShopLooks, type ShopSortId } from "@/lib/fb-rank";
import { filterLooksByQuery, LOOK_SEARCH_NO_MATCH } from "@/lib/look-search";
import type { ShopLook } from "@/lib/shop-look";

const FILTER_NO_MATCH =
  "Không có look nào hợp bộ lọc · No looks match those filters.";

const SIZE_PARAM = "size";
const COLOR_PARAM = "color";
const PRICE_PARAM = "price";

type PriceFilter = "all" | "priced" | "inbox";

const PRICE_FILTERS: ReadonlyArray<{
  id: PriceFilter;
  label: string;
  aria: string;
}> = [
  { id: "all", label: "All", aria: "All prices · Mọi giá" },
  { id: "priced", label: "Priced", aria: "Priced · Có giá niêm yết" },
  {
    id: "inbox",
    label: HOLD_PRICE_LABEL,
    aria: `${HOLD_PRICE_LABEL} · ${HOLD_ASK_LABEL}`,
  },
];

function parseSizeParam(raw: string | null): AsiaSizeLetter[] {
  if (!raw) {
    return [];
  }
  const picked = new Set<AsiaSizeLetter>();
  for (const piece of raw.split(",")) {
    const letter = piece.trim().toUpperCase();
    if (isAsiaSizeLetter(letter)) {
      picked.add(letter);
    }
  }
  return ASIA_SIZE_LETTERS.filter((letter) => picked.has(letter));
}

function parseColorParam(raw: string | null, knownIds: Set<string>): string[] {
  if (!raw) {
    return [];
  }
  const picked: string[] = [];
  for (const piece of raw.split(",")) {
    const id = piece.trim();
    if (id && knownIds.has(id) && !picked.includes(id)) {
      picked.push(id);
    }
  }
  return picked;
}

function parsePriceParam(raw: string | null): PriceFilter {
  return raw === "priced" || raw === "inbox" ? raw : "all";
}

const FILTER_CHIP =
  "inline-flex min-h-11 cursor-pointer touch-manipulation select-none items-center justify-center rounded-full border px-4 text-[12px] font-medium tracking-[0.08em] focus-within:outline focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-gold";

function chipTone(checked: boolean): string {
  return checked
    ? "border-gold/70 bg-blush text-ink"
    : "border-ink/15 text-muted hover-hover:hover:border-ink/30 hover-hover:hover:text-ink";
}

function FilteredLooks({
  products,
  motionKey,
  sort,
}: {
  products: ShopLook[];
  motionKey: string;
  sort: ShopSortId;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { draft, setDraft } = useShopSearch();
  const needle = (draft ?? "").trim();

  // NOTE: availability is intentionally NOT a filter — the customer-safe
  // ShopLook payload strips ops fields (status/qty), so stock is unknown here.
  const sizeOptions = useMemo(
    () =>
      ASIA_SIZE_LETTERS.filter((letter) =>
        products.some((product) => product.sizes.includes(letter)),
      ),
    [products],
  );
  const colorOptions = useMemo(() => {
    const seen = new Map<string, string>();
    for (const product of products) {
      for (const color of product.colors) {
        if (!seen.has(color.id)) {
          seen.set(color.id, color.name);
        }
      }
    }
    return [...seen.entries()].map(([id, name]) => ({ id, name }));
  }, [products]);
  const colorIds = useMemo(
    () => new Set(colorOptions.map((color) => color.id)),
    [colorOptions],
  );

  // URL is the source of truth: filters are shareable and Back-button safe.
  const sizes = useMemo(
    () => parseSizeParam(searchParams.get(SIZE_PARAM)),
    [searchParams],
  );
  const colors = useMemo(
    () => parseColorParam(searchParams.get(COLOR_PARAM), colorIds),
    [searchParams, colorIds],
  );
  const price = parsePriceParam(searchParams.get(PRICE_PARAM));

  const searched = useMemo(
    () => filterLooksByQuery(products, needle),
    [products, needle],
  );
  const filtered = useMemo(
    () =>
      searched.filter((product) => {
        if (
          sizes.length > 0 &&
          !product.sizes.some((size) => sizes.includes(size))
        ) {
          return false;
        }
        if (
          colors.length > 0 &&
          !product.colors.some((color) => colors.includes(color.id))
        ) {
          return false;
        }
        if (price === "priced" && product.priceUsd === null) {
          return false;
        }
        if (price === "inbox" && product.priceUsd !== null) {
          return false;
        }
        return true;
      }),
    [searched, sizes, colors, price],
  );
  const visible = useMemo(
    () => sortShopLooks(filtered, sort),
    [filtered, sort],
  );

  const applyFilters = useCallback(
    (next: {
      sizes: AsiaSizeLetter[];
      colors: string[];
      price: PriceFilter;
    }) => {
      const params = new URLSearchParams(searchParams.toString());
      if (next.sizes.length > 0) {
        params.set(SIZE_PARAM, next.sizes.join(","));
      } else {
        params.delete(SIZE_PARAM);
      }
      if (next.colors.length > 0) {
        params.set(COLOR_PARAM, next.colors.join(","));
      } else {
        params.delete(COLOR_PARAM);
      }
      if (next.price !== "all") {
        params.set(PRICE_PARAM, next.price);
      } else {
        params.delete(PRICE_PARAM);
      }
      const qs = params.toString();
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    },
    [pathname, router, searchParams],
  );

  function toggleSize(size: AsiaSizeLetter) {
    const next = sizes.includes(size)
      ? sizes.filter((entry) => entry !== size)
      : [...sizes, size];
    applyFilters({ sizes: next, colors, price });
  }

  function toggleColor(id: string) {
    const next = colors.includes(id)
      ? colors.filter((entry) => entry !== id)
      : [...colors, id];
    applyFilters({ sizes, colors: next, price });
  }

  function choosePrice(next: PriceFilter) {
    if (next !== price) {
      applyFilters({ sizes, colors, price: next });
    }
  }

  function clearFilters() {
    applyFilters({ sizes: [], colors: [], price: "all" });
  }

  function clearSearchAndFilters() {
    setDraft(null);
    clearFilters();
  }

  const activeCount =
    sizes.length + colors.length + (price === "all" ? 0 : 1);
  const filtering = activeCount > 0;
  const searching = needle.length > 0;
  const searchMissed = searching && searched.length === 0;
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const priceName = useId();
  const filterKey = `${sizes.join(",")}|${colors.join(",")}|${price}`;

  return (
    <div>
      <div className="mt-4">
        <button
          type="button"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen((value) => !value)}
          data-testid="catalog-filter-toggle"
          className="inline-flex min-h-11 touch-manipulation select-none items-center gap-2 rounded-full border border-ink/15 px-4 text-[11px] font-medium uppercase tracking-[0.16em] text-ink"
        >
          <span aria-hidden>{open ? "–" : "+"}</span>
          <span>Bộ lọc · Filters</span>
          {activeCount > 0 ? (
            <span
              className="inline-flex min-h-6 min-w-6 items-center justify-center rounded-full bg-gold/20 px-1.5 text-[11px] tabular-nums"
              aria-label={`${activeCount} active`}
            >
              {activeCount}
            </span>
          ) : null}
        </button>
        <div id={panelId} hidden={!open} className="mt-4 border-y border-ink/10 py-5">
          {sizeOptions.length > 0 ? (
            <fieldset>
              <legend className="text-[11px] font-medium uppercase tracking-[0.16em] text-muted">
                Size · Kích cỡ
              </legend>
              <div className="mt-2.5 flex flex-wrap gap-2">
                {sizeOptions.map((size) => {
                  const checked = sizes.includes(size);
                  return (
                    <label
                      key={size}
                      className={`${FILTER_CHIP} min-w-11 ${chipTone(checked)}`}
                    >
                      <input
                        type="checkbox"
                        className="sr-only"
                        checked={checked}
                        onChange={() => toggleSize(size)}
                      />
                      <span translate="no">{size}</span>
                    </label>
                  );
                })}
              </div>
            </fieldset>
          ) : null}
          {colorOptions.length > 0 ? (
            <fieldset className="mt-5">
              <legend className="text-[11px] font-medium uppercase tracking-[0.16em] text-muted">
                Màu · Color
              </legend>
              <div className="mt-2.5 flex flex-wrap gap-2">
                {colorOptions.map((color) => {
                  const checked = colors.includes(color.id);
                  return (
                    <label
                      key={color.id}
                      className={`${FILTER_CHIP} ${chipTone(checked)}`}
                    >
                      <input
                        type="checkbox"
                        className="sr-only"
                        checked={checked}
                        onChange={() => toggleColor(color.id)}
                      />
                      <span translate="no">{color.name}</span>
                    </label>
                  );
                })}
              </div>
            </fieldset>
          ) : null}
          <fieldset className="mt-5">
            <legend className="text-[11px] font-medium uppercase tracking-[0.16em] text-muted">
              Giá · Price
            </legend>
            <div className="mt-2.5 flex flex-wrap gap-2">
              {PRICE_FILTERS.map((option) => {
                const checked = price === option.id;
                return (
                  <label
                    key={option.id}
                    className={`${FILTER_CHIP} ${chipTone(checked)}`}
                  >
                    <input
                      type="radio"
                      name={priceName}
                      className="sr-only"
                      checked={checked}
                      onChange={() => choosePrice(option.id)}
                      aria-label={option.aria}
                    />
                    <span translate="no">{option.label}</span>
                  </label>
                );
              })}
            </div>
          </fieldset>
          {filtering ? (
            <div className="mt-5">
              <button
                type="button"
                onClick={clearFilters}
                className="inline-flex min-h-11 touch-manipulation select-none items-center rounded-full border border-ink/15 px-4 text-[11px] font-medium uppercase tracking-[0.16em] text-muted hover-hover:hover:text-ink"
              >
                Xóa bộ lọc · Clear filters
              </button>
            </div>
          ) : null}
        </div>
      </div>
      {filtering || searching ? (
        <p
          className="mt-4 text-[11px] uppercase tracking-[0.16em] text-muted tabular-nums"
          aria-live="polite"
          translate="no"
        >
          Hiển thị {visible.length} / {products.length} looks · Showing{" "}
          {visible.length} of {products.length}
        </p>
      ) : null}
      <div className="mt-8 overflow-hidden">
        <ContentWaveLooks>
          {visible.length === 0 ? (
            <div>
              <ShopEmpty
                title="Looks"
                body={searchMissed ? LOOK_SEARCH_NO_MATCH : FILTER_NO_MATCH}
              />
              <div className="mt-6 flex justify-center">
                <button
                  type="button"
                  onClick={searchMissed ? clearSearchAndFilters : clearFilters}
                  className="min-h-11 touch-manipulation select-none border-y border-gold/45 px-4 py-2 text-[11px] uppercase tracking-[0.16em] text-ink hover-hover:hover:border-gold"
                >
                  {searchMissed
                    ? "Xóa tìm kiếm · Clear search"
                    : "Xóa bộ lọc · Clear filters"}
                </button>
              </div>
            </div>
          ) : (
            <AnimatedProductGrid
              products={visible}
              motionKey={`${motionKey}-${sort}-${needle}-${filterKey}`}
            />
          )}
        </ContentWaveLooks>
      </div>
    </div>
  );
}

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

  return (
    <div data-shop-sort={sort} data-shop-search={needle || undefined}>
      <LooksSortChips sort={sort} onChange={setSort} />
      <Suspense fallback={null}>
        <FilteredLooks products={products} motionKey={motionKey} sort={sort} />
      </Suspense>
    </div>
  );
}
