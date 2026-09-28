"use client";

import type { KeyboardEvent, ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { AnimatedProductGrid } from "@/components/animated-product-grid";
import { useCategorySpy } from "@/components/category-spy";
import { ContentWaveLooks, useContentWave } from "@/components/content-wave";
import { LooksSortChips } from "@/components/looks-sort";
import { SearchResultsBar } from "@/components/search-results-bar";
import { CategorySuggestChips } from "@/components/category-suggest-chips";
import { HScrollCue } from "@/components/h-scroll-cue";
import { ShopEmpty } from "@/components/shop-empty";
import { SizeFilterChips } from "@/components/size-filter";
import { useShopSearch } from "@/components/shop-search";
import type { AsiaSizeLetter } from "@/lib/asia-size";
import { categoryAriaLabel, categoryFilterLabel, categorySectionId, TYPE_SLUGS } from "@/lib/categories";
import { DEFAULT_SHOP_SORT, sortShopLooks, type ShopSortId } from "@/lib/fb-rank";
import { scrollChromeChildIntoView } from "@/lib/gallery-snap";
import { collectionEmptyCopy, FEATURED_ALL_ARIA, lookCountLabel } from "@/lib/look-count";
import { filterLooksByQuery, LOOK_SEARCH_TAB_EMPTY, shopSearchNeedle } from "@/lib/look-search";
import { easeOutFast, slideDirection } from "@/lib/motion";
import { collectShopSizes } from "@/lib/shop-sizes";
import type { MaLetter } from "@/lib/ma";
import type { ShopLook } from "@/lib/shop-look";

type Filter = "all" | MaLetter;

function tabId(filter: Filter): string {
  return `featured-tab-${filter}`;
}

export function FeaturedBoard({
  products,
  types,
  committedQuery = "",
  landingType = null,
}: {
  products: ShopLook[];
  types: MaLetter[];
  committedQuery?: string;
  landingType?: MaLetter | null;
}) {
  const [filter, setFilter] = useState<Filter>("all");
  const [section, setSection] = useState<Filter>(landingType ?? "all");
  const [size, setSize] = useState<AsiaSizeLetter | null>(null);
  const [sort, setSort] = useState<ShopSortId>(DEFAULT_SHOP_SORT);
  const [direction, setDir] = useState(1);
  const tabRailRef = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const wave = useContentWave();
  const { setActive } = useCategorySpy();
  const { draft, clearSearch } = useShopSearch();
  const needle = shopSearchNeedle(draft, committedQuery);
  const browsing = needle.trim() === "";
  const order = useMemo(() => ["all" as const, ...types], [types]);
  const searched = useMemo(() => filterLooksByQuery(products, needle), [needle, products]);
  const inCategory = useMemo(
    () => (filter === "all" ? searched : searched.filter((product) => product.type === filter)),
    [filter, searched],
  );
  const sizeOptions = useMemo(
    () => collectShopSizes(browsing ? searched : inCategory),
    [browsing, inCategory, searched],
  );
  const activeSize = size && sizeOptions.includes(size) ? size : null;
  const visible = useMemo(() => {
    const filtered = activeSize
      ? inCategory.filter((product) => product.sizes.includes(activeSize))
      : inCategory;
    return sortShopLooks(filtered, sort);
  }, [activeSize, inCategory, sort]);
  const sections = useMemo(() => {
    const next = new Map<MaLetter, ShopLook[]>();
    for (const type of types) {
      const inType = searched.filter((product) => product.type === type);
      const sized = activeSize
        ? inType.filter((product) => product.sizes.includes(activeSize))
        : inType;
      next.set(type, sortShopLooks(sized, sort));
    }
    return next;
  }, [activeSize, searched, sort, types]);
  const counts = useMemo(() => {
    const next: Record<string, number> = { all: searched.length };
    for (const type of types) {
      next[type] = searched.filter((product) => product.type === type).length;
    }
    return next;
  }, [searched, types]);
  const browseCount = useMemo(() => {
    let total = 0;
    for (const type of types) {
      total += sections.get(type)?.length ?? 0;
    }
    return total;
  }, [sections, types]);
  const countLabel = lookCountLabel(browsing ? browseCount : visible.length);

  useEffect(() => {
    if (!browsing) {
      setActive(null);
      return;
    }
    let frame = 0;
    const update = () => {
      frame = 0;
      const chrome = document.querySelector("[data-testid='shop-chrome']");
      const rail = tabRailRef.current;
      const chromeBottom = chrome?.getBoundingClientRect().bottom ?? 0;
      const railRect = rail?.getBoundingClientRect();
      const railTop = railRect?.top ?? chromeBottom;
      const railBottom = railRect?.bottom ?? chromeBottom;
      const railStuck = railTop <= chromeBottom + 2;
      const line = (railStuck ? railBottom : chromeBottom) + 20;
      let next: Filter = "all";
      for (const type of types) {
        const node = document.getElementById(categorySectionId(type));
        if (!node) {
          continue;
        }
        if (node.getBoundingClientRect().top <= line) {
          next = type;
        }
      }
      setSection((current) => (current === next ? current : next));
      setActive(next);
    };
    const onScroll = () => {
      if (frame) {
        return;
      }
      frame = window.requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("hashchange", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("hashchange", onScroll);
      if (frame) {
        window.cancelAnimationFrame(frame);
      }
    };
  }, [browsing, setActive, types]);

  useEffect(() => {
    return () => setActive(null);
  }, [setActive]);

  useEffect(() => {
    if (!browsing) {
      return;
    }
    scrollChromeChildIntoView(tabRailRef.current, document.getElementById(tabId(section)));
  }, [browsing, section]);

  function choose(next: Filter) {
    if (next === filter) {
      return;
    }
    const from = order.indexOf(filter);
    const to = order.indexOf(next);
    setDir(slideDirection(from, to));
    setFilter(next);
    wave.play();
    requestAnimationFrame(() => {
      scrollChromeChildIntoView(tabRailRef.current, document.getElementById(tabId(next)));
    });
  }

  function moveChipFocus(event: KeyboardEvent<HTMLElement>, current: Filter) {
    const index = order.indexOf(current);
    if (index < 0) {
      return;
    }
    let nextIndex = index;
    switch (event.key) {
      case "ArrowRight":
        nextIndex = (index + 1) % order.length;
        break;
      case "ArrowLeft":
        nextIndex = (index - 1 + order.length) % order.length;
        break;
      case "Home":
        nextIndex = 0;
        break;
      case "End":
        nextIndex = order.length - 1;
        break;
      default:
        return;
    }
    const next = order[nextIndex];
    if (!next) {
      return;
    }
    event.preventDefault();
    const chip = document.getElementById(tabId(next));
    chip?.focus();
    scrollChromeChildIntoView(tabRailRef.current, chip);
  }

  function onTabListKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const current = order.indexOf(filter);
    if (current < 0) {
      return;
    }
    let nextIndex = current;
    switch (event.key) {
      case "ArrowRight":
        nextIndex = (current + 1) % order.length;
        break;
      case "ArrowLeft":
        nextIndex = (current - 1 + order.length) % order.length;
        break;
      case "Home":
        nextIndex = 0;
        break;
      case "End":
        nextIndex = order.length - 1;
        break;
      default:
        return;
    }
    const next = order[nextIndex];
    if (!next) {
      return;
    }
    event.preventDefault();
    choose(next);
    const button = event.currentTarget.querySelector<HTMLButtonElement>(`#${tabId(next)}`);
    button?.focus();
  }

  return (
    <section
      id="featured-collection"
      aria-labelledby="looks-heading"
      className="bg-paper ky-gutter pb-10 pt-4 sm:pb-12 sm:pt-6 scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)] sm:scroll-mt-[calc(env(safe-area-inset-top,0px)+8.75rem)]"
    >
      <div className="mx-auto max-w-7xl">
        <div className="flex items-end justify-between gap-3">
          <h2
            id="looks-heading"
            data-testid="looks-heading"
            tabIndex={-1}
            className="text-left font-display text-[2.15rem] font-medium leading-[1.08] tracking-[0.02em] text-balance text-ink outline-none sm:text-[2.75rem]"
            translate="no"
          >
            Looks
          </h2>
          <p
            data-testid="looks-count"
            className="mb-1 max-w-full shrink-0 truncate whitespace-nowrap text-[11px] uppercase tracking-[0.16em] text-muted tabular-nums"
            aria-live="polite"
            translate="no"
          >
            <AnimatePresence mode="wait" initial={false}>
              <motion.span
                key={countLabel}
                className="inline-block"
                initial={reduced ? false : { opacity: 0 }}
                animate={{ opacity: 1, y: 0 }}
                exit={reduced ? { opacity: 1, y: 0, transition: { duration: 0 } } : { opacity: 0 }}
                transition={{ duration: reduced ? 0 : 0.18 }}
              >
                {countLabel}
              </motion.span>
            </AnimatePresence>
          </p>
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-x-1 gap-y-1">
          <LooksSortChips sort={sort} onChange={setSort} />
          <SizeFilterChips sizes={sizeOptions} selected={activeSize} onChange={setSize} />
        </div>
        <HScrollCue className={browsing ? "ky-h-scroll-cue sc-cat-rail mt-1" : "ky-h-scroll-cue mt-1"}>
        <LayoutGroup id="featured-tabs">
          <motion.div
            ref={tabRailRef}
            layoutScroll
            className="featured-tab-rule ky-gutter-bleed min-w-0 max-w-full overflow-x-auto pb-1 tab-scroll"
          >
            {browsing ? (
              <nav
                aria-label="Lọc looks · Filter looks"
                onKeyDown={(event) => moveChipFocus(event, section)}
                className="flex min-w-max flex-nowrap items-center justify-start gap-x-3"
              >
                <FilterTab
                  id={tabId("all")}
                  href="#featured-collection"
                  active={section === "all"}
                  count={counts.all ?? 0}
                  position={1}
                  setSize={order.length}
                  onClick={() => wave.play()}
                  reduced={Boolean(reduced)}
                  ariaName={FEATURED_ALL_ARIA}
                >
                  All
                </FilterTab>
                {types.map((type, typeIndex) => (
                  <FilterTab
                    key={type}
                    id={tabId(type)}
                    href={`#${categorySectionId(type)}`}
                    active={section === type}
                    count={counts[type] ?? 0}
                    position={typeIndex + 2}
                    setSize={order.length}
                    onClick={() => wave.play()}
                    reduced={Boolean(reduced)}
                    ariaName={categoryAriaLabel(type)}
                  >
                    {categoryFilterLabel(type)}
                  </FilterTab>
                ))}
              </nav>
            ) : (
            <div
              role="tablist"
              aria-orientation="horizontal"
              aria-label="Lọc looks · Filter looks"
              onKeyDown={onTabListKeyDown}
              className="flex min-w-max flex-nowrap items-center justify-start gap-x-3"
            >
              <FilterTab
                id={tabId("all")}
                active={filter === "all"}
                count={counts.all ?? 0}
                position={1}
                setSize={order.length}
                onClick={() => choose("all")}
                reduced={Boolean(reduced)}
                ariaName={FEATURED_ALL_ARIA}
              >
                All
              </FilterTab>
              {types.map((type, typeIndex) => (
                <FilterTab
                  key={type}
                  id={tabId(type)}
                  active={filter === type}
                  count={counts[type] ?? 0}
                  position={typeIndex + 2}
                  setSize={order.length}
                  onClick={() => choose(type)}
                  reduced={Boolean(reduced)}
                  ariaName={categoryAriaLabel(type)}
                >
                  {categoryFilterLabel(type)}
                </FilterTab>
              ))}
            </div>
            )}
          </motion.div>
        </LayoutGroup>
        </HScrollCue>
        <SearchResultsBar query={needle} />
        {browsing ? (
          <div id="featured-panel" data-shop-sort={sort} data-shop-size={activeSize ?? undefined} className="mt-4">
            <ContentWaveLooks>
              {types.map((type, index) => {
                const items = sections.get(type) ?? [];
                const id = categorySectionId(type);
                const label = categoryFilterLabel(type);
                return (
                  <section
                    key={type}
                    id={id}
                    aria-labelledby={`${id}-title`}
                    data-testid="category-section"
                    className="sc-cat-section mt-8 first:mt-0"
                  >
                    <h3
                      id={`${id}-title`}
                      tabIndex={-1}
                      className="mb-2 font-display text-[1.45rem] font-medium leading-[1.08] tracking-[0.02em] text-balance text-ink outline-none"
                      translate="no"
                    >
                      {label}
                    </h3>
                    {items.length === 0 ? (
                      <ShopEmpty
                        {...(activeSize
                          ? {
                              title: label,
                              body: `Không có size ${activeSize} · No size ${activeSize} in this view.`,
                            }
                          : collectionEmptyCopy(label, TYPE_SLUGS[type]))}
                      />
                    ) : (
                      <AnimatedProductGrid
                        products={items}
                        motionKey={`${type}-${sort}-${activeSize ?? ""}`}
                        eagerCount={index === 0 ? 2 : 0}
                      />
                    )}
                  </section>
                );
              })}
            </ContentWaveLooks>
          </div>
        ) : (
        <div
          id="featured-panel"
          role="tabpanel"
          aria-labelledby={tabId(filter)}
          data-shop-sort={sort}
          data-shop-size={activeSize ?? undefined}
          data-shop-search={needle.trim() || undefined}
          className="mt-4 overflow-hidden"
        >
          <ContentWaveLooks>
            {visible.length === 0 ? (
              <ShopEmpty
                {...(needle.trim() && searched.length === 0
                  ? {
                      title: filter === "all" ? "Looks" : categoryFilterLabel(filter),
                      body: `Không thấy “${needle.trim().slice(0, 40)}” · No results for “${needle.trim().slice(0, 40)}”.`,
                    }
                  : activeSize && inCategory.length > 0
                    ? {
                        title: filter === "all" ? "Looks" : categoryFilterLabel(filter),
                        body: `Không có size ${activeSize} · No size ${activeSize} in this view.`,
                      }
                  : needle.trim()
                    ? {
                        title: filter === "all" ? "Looks" : categoryFilterLabel(filter),
                        body: LOOK_SEARCH_TAB_EMPTY,
                      }
                    : filter === "all"
                      ? {
                          title: "Looks",
                          body: "Chưa có looks trên lookbook · No looks listed.",
                        }
                      : collectionEmptyCopy(categoryFilterLabel(filter), TYPE_SLUGS[filter]))}
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
                        <button
                          type="button"
                          className="inline-flex min-h-11 touch-manipulation items-center rounded-full border border-gold/45 px-4 text-[13px] text-ink"
                          onClick={() => {
                            choose("all");
                            setSize(null);
                            clearSearch();
                          }}
                        >
                          Xem tất cả · Browse all
                        </button>
                      </div>
                      {needle.trim() && searched.length === 0 ? (
                        <CategorySuggestChips types={types} className="mt-5" />
                      ) : null}
                    </div>
                  ) : null
                }
              />
            ) : (
              <AnimatedProductGrid products={visible} motionKey={`${filter}-${sort}-${needle}`} direction={direction} />
            )}
          </ContentWaveLooks>
        </div>
        )}
      </div>
    </section>
  );
}

function FilterTab({
  id,
  href,
  active,
  count,
  position,
  setSize,
  onClick,
  reduced,
  children,
  ariaName,
}: {
  id: string;
  href?: string;
  active: boolean;
  count: number;
  position: number;
  setSize: number;
  onClick: () => void;
  reduced: boolean;
  children: ReactNode;
  ariaName: string;
}) {
  const className = `relative inline-flex min-h-11 min-w-11 shrink-0 touch-manipulation select-none items-end justify-center whitespace-nowrap px-2.5 pb-2 text-[11px] font-medium uppercase tracking-[0.16em] motion-safe:transition-colors motion-safe:duration-150 ${
    active ? "text-ink" : "text-muted hover-hover:hover:text-ink"
  }`;
  const body = (
    <>
      {active ? (
        <span className="liquid-glass-chip pointer-events-none absolute inset-x-0 top-0.5 bottom-1 -z-0 rounded-md" aria-hidden />
      ) : null}
      <span className="relative z-[1]">{children}</span>
      <span className={`relative z-[1] ml-1.5 tabular-nums tracking-[0.08em] ${active ? "text-gold-ink" : "text-muted"}`} aria-hidden>
        {count}
      </span>
      <span className="sr-only">{`, ${ariaName}, ${lookCountLabel(count)}`}</span>
      {active ? (
        <motion.span
          layoutId={reduced ? undefined : "featured-tab"}
          className="featured-tab-film pointer-events-none absolute inset-x-0 bottom-0 h-px bg-gold"
          transition={reduced ? { duration: 0 } : easeOutFast}
          aria-hidden
        />
      ) : null}
    </>
  );

  if (href) {
    return (
      <a
        id={id}
        href={href}
        aria-current={active ? "true" : undefined}
        onClick={onClick}
        data-testid="featured-filter-tab"
        translate="no"
        className={className}
      >
        {body}
      </a>
    );
  }

  return (
    <button
      id={id}
      type="button"
      role="tab"
      aria-selected={active}
      aria-controls="featured-panel"
      aria-posinset={position}
      aria-setsize={setSize}
      tabIndex={active ? 0 : -1}
      onClick={onClick}
      data-testid="featured-filter-tab"
      translate="no"
      className={className}
    >
      {body}
    </button>
  );
}
