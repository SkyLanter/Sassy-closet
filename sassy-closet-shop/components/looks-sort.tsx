"use client";

import type { KeyboardEvent } from "react";
import {
  DEFAULT_SHOP_SORT,
  SHOP_SORT_OPTIONS,
  type ShopSortId,
} from "@/lib/fb-rank";

export { DEFAULT_SHOP_SORT, type ShopSortId };

export function LooksSortChips({
  sort,
  onChange,
}: {
  sort: ShopSortId;
  onChange: (next: ShopSortId) => void;
}) {
  const currentIndex = SHOP_SORT_OPTIONS.findIndex((option) => option.id === sort);

  function onGroupKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const count = SHOP_SORT_OPTIONS.length;
    let nextIndex = currentIndex < 0 ? 0 : currentIndex;
    switch (event.key) {
      case "ArrowRight":
        nextIndex = (nextIndex + 1) % count;
        break;
      case "ArrowLeft":
        nextIndex = (nextIndex - 1 + count) % count;
        break;
      case "Home":
        nextIndex = 0;
        break;
      case "End":
        nextIndex = count - 1;
        break;
      default:
        return;
    }
    const next = SHOP_SORT_OPTIONS[nextIndex];
    if (!next) {
      return;
    }
    event.preventDefault();
    onChange(next.id);
    const button = event.currentTarget.querySelector<HTMLButtonElement>(`#looks-sort-${next.id}`);
    button?.focus();
  }

  return (
    <div
      role="radiogroup"
      aria-label="Sort looks"
      data-testid="looks-sort"
      data-active={sort}
      onKeyDown={onGroupKeyDown}
      className="mt-4 flex min-w-0 flex-wrap items-center gap-2"
    >
      {SHOP_SORT_OPTIONS.map((option) => {
        const active = option.id === sort;
        return (
          <button
            key={option.id}
            id={`looks-sort-${option.id}`}
            type="button"
            role="radio"
            aria-checked={active}
            aria-label={option.aria}
            data-testid={`looks-sort-${option.id}`}
            tabIndex={active ? 0 : -1}
            onClick={() => onChange(option.id)}
            translate="no"
            className={`relative min-h-11 shrink-0 touch-manipulation select-none whitespace-nowrap rounded-md px-3 text-[11px] font-medium uppercase tracking-[0.16em] motion-safe:transition-colors motion-safe:duration-300 ${
              active ? "text-ink" : "text-muted hover-hover:hover:text-ink"
            }`}
          >
            {active ? (
              <span className="liquid-glass-chip pointer-events-none absolute inset-0 -z-0 rounded-md" aria-hidden />
            ) : null}
            <span className="relative z-[1]">{option.label}</span>
          </button>
        );
      })}
    </div>
  );
}
