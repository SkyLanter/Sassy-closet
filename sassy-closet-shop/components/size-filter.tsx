"use client";

import type { KeyboardEvent } from "react";
import type { AsiaSizeLetter } from "@/lib/asia-size";

export function SizeFilterChips({
  sizes,
  selected,
  onChange,
}: {
  sizes: readonly AsiaSizeLetter[];
  selected: AsiaSizeLetter | null;
  onChange: (next: AsiaSizeLetter | null) => void;
}) {
  if (sizes.length === 0) {
    return null;
  }

  const options: Array<AsiaSizeLetter | null> = [null, ...sizes];
  const currentIndex = options.findIndex((option) => option === selected);

  function onGroupKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const count = options.length;
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
    const next = options[nextIndex];
    event.preventDefault();
    onChange(next ?? null);
    const button = event.currentTarget.querySelector<HTMLButtonElement>(
      `#size-filter-${next ?? "all"}`,
    );
    button?.focus();
  }

  return (
    <div
      role="radiogroup"
      aria-label="Lọc cỡ · Filter by size"
      data-testid="size-filter"
      data-active={selected ?? "all"}
      onKeyDown={onGroupKeyDown}
      className="mt-3 flex min-w-0 flex-wrap items-center gap-2"
    >
      {options.map((option) => {
        const active = option === selected;
        const id = `size-filter-${option ?? "all"}`;
        const label = option ?? "All";
        return (
          <button
            key={id}
            id={id}
            type="button"
            role="radio"
            aria-checked={active}
            aria-label={option ? `Size ${option}` : "Tất cả cỡ · All sizes"}
            data-testid={`size-filter-${option ?? "all"}`}
            tabIndex={active ? 0 : -1}
            onClick={() => onChange(option)}
            translate="no"
            className={`sc-press relative min-h-11 min-w-11 shrink-0 touch-manipulation select-none whitespace-nowrap rounded-md px-3 text-[11px] font-medium uppercase tracking-[0.16em] ${
              active ? "text-ink" : "text-muted hover-hover:hover:text-ink"
            }`}
          >
            {active ? (
              <span className="liquid-glass-chip pointer-events-none absolute inset-0 -z-0 rounded-md" aria-hidden />
            ) : null}
            <span className="relative z-[1]">{label}</span>
          </button>
        );
      })}
    </div>
  );
}
