"use client";

import type { KeyboardEvent } from "react";
import { useLayoutEffect, useRef } from "react";
import { LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { useContentWave } from "@/components/content-wave";
import { colorShopLabel } from "@/lib/colors";
import { scrollChromeChildIntoView } from "@/lib/gallery-snap";
import { springSoft } from "@/lib/motion";
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
      <div
        ref={railRef}
        className={`flex min-w-0 max-w-full flex-nowrap overflow-x-auto tab-scroll scroll-px-2 ${compact ? "gap-1.5" : "gap-2"}`}
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
              aria-pressed={selected}
              tabIndex={tabbable ? 0 : -1}
              aria-posinset={index + 1}
              aria-setsize={colors.length}
              data-testid="shop-color-chip"
              data-color-id={color.id}
              aria-label={label}
              onClick={() => {
                onSelect(color.id);
                if (color.id !== selectedId) {
                  wave.play();
                }
              }}
              className={`ky-color-chip liquid-glass-chip relative inline-flex shrink-0 items-center touch-manipulation select-none whitespace-nowrap px-3 font-medium uppercase ${
                compact ? "min-h-8 text-[10px] tracking-[0.12em]" : "min-h-11 text-[11px] tracking-[0.16em]"
              } ${selected ? "text-ink" : "text-muted hover-hover:hover:text-ink"}`}
              translate="no"
            >
              <span className="relative z-[1]">{label}</span>
              {selected && animateSelection ? (
                <motion.span
                  layoutId={lineLayoutId}
                  className="absolute inset-x-0 bottom-0 h-px bg-gold"
                  transition={springSoft}
                  aria-hidden
                />
              ) : null}
              {selected && !animateSelection ? (
                <span className="absolute inset-x-0 bottom-0 h-px bg-gold" aria-hidden />
              ) : null}
            </button>
          );
        })}
      </div>
    </LayoutGroup>
  );
}
