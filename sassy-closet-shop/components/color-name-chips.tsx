"use client";

import type { KeyboardEvent } from "react";
import { useLayoutEffect, useRef } from "react";
import { LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { useContentWave } from "@/components/content-wave";
import { HScrollCue } from "@/components/h-scroll-cue";
import { colorShopLabel } from "@/lib/colors";
import { scrollChromeChildIntoView } from "@/lib/gallery-snap";
import { easeOutFast } from "@/lib/motion";
import { COLOR_FIELD_LEGEND } from "@/lib/pdp-copy";
import type { ProductColor } from "@/lib/types";

export function ColorNameChips({
  colors,
  selectedId,
  onSelect,
  size = "md",
  motionGroupId,
  hairlineLayoutId,
}: {
  colors: ProductColor[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  size?: "sm" | "md";
  motionGroupId?: string;
  hairlineLayoutId?: string;
}) {
  const reduced = useReducedMotion();
  const wave = useContentWave();
  const railRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    scrollChromeChildIntoView(
      railRef.current,
      railRef.current?.querySelector<HTMLElement>('[aria-checked="true"]') ?? null,
    );
  }, [selectedId]);

  if (colors.length === 0) {
    return null;
  }

  const compact = size === "sm";
  const lineLayoutId = hairlineLayoutId ?? (motionGroupId ? `${motionGroupId}-hair` : undefined);
  const animateSelection = Boolean(lineLayoutId) && !reduced;
  const selectedIndex = colors.findIndex((color) => color.id === selectedId);
  const selectedColor = selectedIndex >= 0 ? colors[selectedIndex] : undefined;
  const noteId =
    size !== "sm" && selectedColor?.note.trim() && motionGroupId
      ? `${motionGroupId}-color-note`
      : undefined;

  function onGroupKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const count = colors.length;
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
    const next = colors[nextIndex];
    if (!next) {
      return;
    }
    event.preventDefault();
    onSelect(next.id);
    if (next.id !== selectedId) {
      wave.play();
    }
    const button = event.currentTarget.querySelector<HTMLButtonElement>(
      `[data-color-id="${next.id}"]`,
    );
    button?.focus();
  }

  return (
    <LayoutGroup id={motionGroupId}>
      <HScrollCue className="ky-h-scroll-cue min-w-0 max-w-full">
        <div
          ref={railRef}
          className="flex w-full min-w-0 max-w-full flex-nowrap gap-1 scroll-px-2 overflow-x-auto tab-scroll"
          role="radiogroup"
          aria-orientation="horizontal"
          aria-label={COLOR_FIELD_LEGEND}
          aria-describedby={noteId}
          onKeyDown={onGroupKeyDown}
        >
          {colors.map((color, index) => {
            const selected = selectedId === color.id;
            const label = colorShopLabel(color, index);
            const tabbable = selected || (selectedId === null && index === 0);
            return (
              <button
                key={color.id}
                type="button"
                role="radio"
                aria-checked={selected}
                tabIndex={tabbable ? 0 : -1}
                data-testid="shop-color-chip"
                data-color-id={color.id}
                aria-label={label}
              aria-posinset={index + 1}
              aria-setsize={colors.length}
                onClick={() => {
                  onSelect(color.id);
                  if (color.id !== selectedId) {
                    wave.play();
                  }
                }}
                className={`sc-chip-hit ky-color-chip liquid-glass-chip sc-press relative inline-flex min-h-11 min-w-11 shrink-0 items-center justify-center touch-manipulation select-none px-0.5 font-medium uppercase ${
                  compact ? "text-[11px] tracking-[0.12em]" : "text-[11px] tracking-[0.16em]"
                } ${selected ? "text-ink" : "text-muted hover-hover:hover:text-ink"}`}
                translate="no"
              >
                <span
                  className={`sc-chip-face relative z-[1] inline-flex min-h-8 max-w-full items-center rounded-full border px-3 ${
                    selected ? "border-ink text-ink" : "border-line text-muted"
                  }`}
                >
                  <span className="truncate whitespace-nowrap">{label}</span>
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
