"use client";

import type { KeyboardEvent } from "react";
import { useMemo, useRef, useState } from "react";
import { AnimatePresence, LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { AnimatedProductGrid } from "@/components/animated-product-grid";
import { ContentWaveLooks, useContentWave } from "@/components/content-wave";
import { LooksSortChips } from "@/components/looks-sort";
import { ShopEmpty } from "@/components/shop-empty";
import { useShopSearch } from "@/components/shop-search";
import { categoryAriaLabel, categoryCopy, TYPE_SLUGS } from "@/lib/categories";
import { DEFAULT_SHOP_SORT, sortShopLooks, type ShopSortId } from "@/lib/fb-rank";
import { scrollChromeChildIntoView } from "@/lib/gallery-snap";
import { collectionEmptyCopy, FEATURED_ALL_ARIA, lookCountLabel } from "@/lib/look-count";
import { filterLooksByQuery, LOOK_SEARCH_NO_MATCH, LOOK_SEARCH_TAB_EMPTY } from "@/lib/look-search";
import { slideDirection, springSoft } from "@/lib/motion";
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
}: {
  products: ShopLook[];
  types: MaLetter[];
  committedQuery?: string;
}) {
  const [filter, setFilter] = useState<Filter>("all");
  const [sort, setSort] = useState<ShopSortId>(DEFAULT_SHOP_SORT);
  const [direction, setDir] = useState(1);
  const tabRailRef = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const wave = useContentWave();
  const { draft } = useShopSearch();
  const needle = draft ?? committedQuery;
  const order = useMemo(() => ["all" as const, ...types], [types]);
  const searched = useMemo(() => filterLooksByQuery(products, needle), [needle, products]);
  const visible = useMemo(() => {
    const filtered =
      filter === "all" ? searched : searched.filter((product) => product.type === filter);
    return sortShopLooks(filtered, sort);
  }, [filter, searched, sort]);
  const counts = useMemo(() => {
    const next: Record<string, number> = { all: searched.length };
    for (const type of types) {
      next[type] = searched.filter((product) => product.type === type).length;
    }
    return next;
  }, [searched, types]);
  const countLabel = lookCountLabel(visible.length);

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
      className="bg-paper ky-gutter py-10 sm:py-12 scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)] sm:scroll-mt-[calc(env(safe-area-inset-top,0px)+8.75rem)]"
    >
      <div className="mx-auto max-w-7xl">
        <h2
          id="looks-heading"
          data-testid="looks-heading"
          tabIndex={-1}
          className="text-left font-display text-[2.15rem] font-medium leading-[1.08] tracking-[0.02em] text-balance text-ink outline-none sm:text-[2.75rem]"
          translate="no"
        >
          Looks
        </h2>
        <LooksSortChips sort={sort} onChange={setSort} />
        <div className="ky-h-scroll-cue mt-5">
        <LayoutGroup id="featured-tabs">
          <motion.div
            ref={tabRailRef}
            layoutScroll
            className="featured-tab-rule ky-gutter-bleed min-w-0 max-w-full overflow-x-auto pb-1 tab-scroll"
          >
            <div
              role="tablist"
              aria-orientation="horizontal"
              aria-label="Lọc looks · Filter looks"
              onKeyDown={onTabListKeyDown}
              className="flex min-w-max flex-nowrap items-center justify-start gap-x-5"
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
                  {categoryCopy(type).label}
                </FilterTab>
              ))}
            </div>
          </motion.div>
        </LayoutGroup>
        </div>
        <p
          className="mx-auto mt-3 max-w-full truncate whitespace-nowrap text-left text-[11px] uppercase tracking-[0.16em] text-muted tabular-nums"
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
        <div
          id="featured-panel"
          role="tabpanel"
          aria-labelledby={tabId(filter)}
          data-shop-sort={sort}
          data-shop-search={needle.trim() || undefined}
          className="mt-8 overflow-hidden"
        >
          <ContentWaveLooks>
            {visible.length === 0 ? (
              <ShopEmpty
                {...(needle.trim()
                  ? {
                      title: filter === "all" ? "Looks" : categoryCopy(filter).label,
                      body: searched.length === 0 ? LOOK_SEARCH_NO_MATCH : LOOK_SEARCH_TAB_EMPTY,
                    }
                  : filter === "all"
                    ? {
                        title: "Looks",
                        body: "Chưa có looks trên lookbook · No looks listed.",
                      }
                    : collectionEmptyCopy(categoryCopy(filter).label, TYPE_SLUGS[filter]))}
              />
            ) : (
              <AnimatedProductGrid products={visible} motionKey={`${filter}-${sort}-${needle}`} direction={direction} />
            )}
          </ContentWaveLooks>
        </div>
      </div>
    </section>
  );
}

function FilterTab({
  id,
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
  active: boolean;
  count: number;
  position: number;
  setSize: number;
  onClick: () => void;
  reduced: boolean;
  children: string;
  ariaName: string;
}) {
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
      aria-label={`${ariaName}, ${lookCountLabel(count)}`}
      translate="no"
      className={`relative min-h-11 shrink-0 touch-manipulation select-none whitespace-nowrap px-2.5 pb-2 text-[11px] font-medium uppercase tracking-[0.16em] motion-safe:transition-colors motion-safe:duration-300 ${
        active ? "text-ink" : "text-muted hover-hover:hover:text-ink"
      }`}
    >
      {active ? (
        <span className="liquid-glass-chip pointer-events-none absolute inset-x-0 top-0.5 bottom-1 -z-0 rounded-md" aria-hidden />
      ) : null}
      <span className="relative z-[1]">{children}</span>
      <span className={`relative z-[1] ml-1.5 tabular-nums tracking-[0.08em] ${active ? "text-gold-deep" : "text-muted/80"}`} aria-hidden>
        {count}
      </span>
      {active ? (
        <motion.span
          layoutId={reduced ? undefined : "featured-tab"}
          className="featured-tab-film pointer-events-none absolute inset-x-0 bottom-0 h-px bg-gold"
          transition={reduced ? { duration: 0 } : springSoft}
          aria-hidden
        />
      ) : null}
    </button>
  );
}
