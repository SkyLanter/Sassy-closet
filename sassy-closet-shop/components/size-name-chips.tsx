"use client";

import type { KeyboardEvent } from "react";
import { useLayoutEffect, useRef } from "react";
import { LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { HScrollCue } from "@/components/h-scroll-cue";
import { scrollChromeChildIntoView } from "@/lib/gallery-snap";
import { easeOutFast } from "@/lib/motion";
import { SIZE_FIELD_LEGEND } from "@/lib/pdp-copy";
import type { AsiaSizeLetter } from "@/lib/asia-size";

export function SizeNameChips({
  sizes,
  selectedId,
  onSelect,
  motionGroupId,
  hairlineLayoutId,
}: {
  sizes: AsiaSizeLetter[];
  selectedId: AsiaSizeLetter | null;
  onSelect: (letter: AsiaSizeLetter) => void;
  motionGroupId?: string;
  hairlineLayoutId?: string;
}) {
  const reduced = useReducedMotion();
  const railRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    scrollChromeChildIntoView(
      railRef.current,
      railRef.current?.querySelector<HTMLElement>('[aria-checked="true"]') ?? null,
    );
  }, [selectedId]);

  if (sizes.length === 0) {
    return null;
  }

  const lineLayoutId = hairlineLayoutId ?? (motionGroupId ? `${motionGroupId}-hair` : undefined);
  const animateSelection = Boolean(lineLayoutId) && !reduced;
  const selectedIndex = sizes.findIndex((letter) => letter === selectedId);

  function onGroupKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const count = sizes.length;
    let nextIndex = selectedIndex;
    switch (event.key) {
      case "ArrowRight":
        nextIndex = selectedIndex < 0 ? 0 : (selectedIndex + 1) % count;
        break;
      case "ArrowLeft":
        nextIndex = selectedIndex < 0 ? count - 1 : (selectedIndex - 1 + count) % count;
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
    const next = sizes[nextIndex];
    if (!next) {
      return;
    }
    event.preventDefault();
    onSelect(next);
    const button = event.currentTarget.querySelector<HTMLButtonElement>(
      `[data-size-letter="${next}"]`,
    );
    button?.focus();
  }

  return (
    <LayoutGroup id={motionGroupId}>
      <HScrollCue className="ky-h-scroll-cue min-w-0 max-w-full">
      <div
        ref={railRef}
        className="flex min-w-0 max-w-full flex-nowrap gap-1 overflow-x-auto tab-scroll scroll-px-2"
        role="radiogroup"
        aria-orientation="horizontal"
        aria-label={SIZE_FIELD_LEGEND}
        onKeyDown={onGroupKeyDown}
      >
        {sizes.map((letter, index) => {
          const selected = selectedId === letter;
          const tabbable = selected || (selectedId === null && index === 0);
          return (
            <button
              key={letter}
              type="button"
              role="radio"
              aria-checked={selected}
              tabIndex={tabbable ? 0 : -1}
              data-testid="shop-size-chip"
              data-size-letter={letter}
              aria-label={letter}
              onClick={() => onSelect(letter)}
              className={`sc-chip-hit ky-color-chip liquid-glass-chip sc-press relative inline-flex min-h-11 min-w-11 shrink-0 items-center justify-center touch-manipulation select-none px-0.5 text-[11px] font-medium uppercase tracking-[0.16em] ${
                selected ? "text-ink" : "text-muted hover-hover:hover:text-ink"
              }`}
              translate="no"
            >
              <span
                className={`sc-chip-face relative z-[1] inline-flex min-h-8 min-w-8 items-center justify-center rounded-full border px-3 whitespace-nowrap ${
                  selected ? "border-ink text-ink" : "border-line text-muted"
                }`}
              >
                {letter}
              </span>
              {selected && animateSelection ? (
                <motion.span
                  layoutId={lineLayoutId}
                  className="pointer-events-none absolute inset-x-3 bottom-1.5 h-px bg-gold"
                  transition={easeOutFast}
                  aria-hidden
                />
              ) : null}
              {selected && !animateSelection ? (
                <span className="pointer-events-none absolute inset-x-3 bottom-1.5 h-px bg-gold" aria-hidden />
              ) : null}
            </button>
          );
        })}
      </div>
      </HScrollCue>
    </LayoutGroup>
  );
}
