"use client";

import { motion, useReducedMotion, useScroll } from "framer-motion";
import type { KeyboardEvent as ReactKeyboardEvent } from "react";
import { useCallback, useId, useLayoutEffect, useRef, useState } from "react";
import {
  animateGalleryScrollTo,
  clampGalleryIndex,
  galleryPeekEdge,
  galleryScrollBehavior,
  GALLERY_ROLL_MS,
  nearestCenteredIndex,
} from "@/lib/gallery-snap";
import { galleryReelLabel, photoIndexLabel, photoPositionLabel } from "@/lib/pdp-copy";

export type PeekSlide = {
  id: string;
  src: string;
  alt: string;
  role: "photo" | "hint";
  colorId?: string | null;
  colorName?: string;
};

type Props = {
  slides: PeekSlide[];
  index: number;
  onIndexChange: (next: number) => void;
  onCenterClick?: () => void;
  ma?: string;
  className?: string;
};

export function GalleryPeekRoll({
  slides,
  index,
  onIndexChange,
  onCenterClick,
  ma,
  className,
}: Props) {
  const reduced = useReducedMotion();
  const railId = useId();
  const portRef = useRef<HTMLDivElement>(null);
  const slideRefs = useRef<Array<HTMLDivElement | null>>([]);
  const indexFromScroll = useRef(index);
  const waterTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelRoll = useRef<(() => void) | null>(null);
  const ignoreScroll = useRef(false);
  const [waterRoll, setWaterRoll] = useState(false);
  const { scrollXProgress } = useScroll({ container: portRef });
  const slideCount = slides.length;
  const safeIndex = clampGalleryIndex(index, slideCount);
  const peeking = slideCount > 1;
  const center = slides[safeIndex];
  const canPrev = peeking && safeIndex > 0;
  const canNext = peeking && safeIndex < slideCount - 1;
  const edge = galleryPeekEdge(safeIndex, slideCount);
  const scrollBehavior = galleryScrollBehavior(Boolean(reduced));

  const pulseWater = useCallback(() => {
    if (reduced || !peeking) {
      return;
    }
    setWaterRoll(true);
    if (waterTimer.current) {
      clearTimeout(waterTimer.current);
    }
    waterTimer.current = setTimeout(() => setWaterRoll(false), GALLERY_ROLL_MS);
  }, [peeking, reduced]);

  const scrollToSlide = useCallback(
    (next: number, behavior: ScrollBehavior) => {
      const el = slideRefs.current[next];
      const port = portRef.current;
      if (!el) {
        return;
      }
      cancelRoll.current?.();
      cancelRoll.current = null;
      if (!port || behavior === "instant" || reduced || !peeking) {
        ignoreScroll.current = false;
        el.scrollIntoView({
          inline: peeking ? "center" : "start",
          block: "nearest",
          behavior: "instant",
        });
        return;
      }
      ignoreScroll.current = true;
      pulseWater();
      cancelRoll.current = animateGalleryScrollTo(port, el, false, () => {
        ignoreScroll.current = false;
        cancelRoll.current = null;
      });
    },
    [peeking, pulseWater, reduced],
  );

  const bootstrapped = useRef(false);

  useLayoutEffect(() => {
    if (!bootstrapped.current) {
      bootstrapped.current = true;
      indexFromScroll.current = safeIndex;
      scrollToSlide(safeIndex, "instant");
      return;
    }
    if (indexFromScroll.current === safeIndex) {
      return;
    }
    indexFromScroll.current = safeIndex;
    scrollToSlide(safeIndex, scrollBehavior);
  }, [peeking, safeIndex, scrollBehavior, scrollToSlide, slides]);

  useLayoutEffect(() => {
    return () => {
      if (waterTimer.current) {
        clearTimeout(waterTimer.current);
      }
      cancelRoll.current?.();
    };
  }, []);

  const onPortScroll = () => {
    const port = portRef.current;
    if (!port || !peeking || ignoreScroll.current) {
      return;
    }
    const next = nearestCenteredIndex(port, slideRefs.current);
    if (next !== indexFromScroll.current) {
      pulseWater();
      indexFromScroll.current = next;
      onIndexChange(next);
    }
  };

  const go = (next: number) => {
    onIndexChange(clampGalleryIndex(next, slideCount));
  };

  function onRailKeyDown(event: ReactKeyboardEvent<HTMLDivElement>) {
    if (!peeking) {
      return;
    }
    switch (event.key) {
      case "ArrowRight":
        event.preventDefault();
        go(safeIndex + 1);
        return;
      case "ArrowLeft":
        event.preventDefault();
        go(safeIndex - 1);
        return;
      case "Home":
        event.preventDefault();
        go(0);
        return;
      case "End":
        event.preventDefault();
        go(slideCount - 1);
        return;
      default:
        return;
    }
  }

  return (
    <div
      data-gallery-roll={peeking ? "peek" : "single"}
      data-gallery-layout="full"
      data-water-roll={peeking && waterRoll ? "1" : "0"}
      data-count={slideCount}
      role={peeking ? "region" : undefined}
      aria-roledescription={peeking ? "carousel" : undefined}
      aria-label={peeking ? galleryReelLabel(ma ?? "Look") : undefined}
      className={`ky-gallery-shell relative h-full w-full select-none bg-[#f3f1ee] ${className ?? ""}`}
    >
      <div className="absolute inset-0 overflow-hidden">
        <div
          ref={portRef}
          id={railId}
          data-testid="gallery-port"
          data-gallery-roll={peeking ? "peek" : "single"}
          data-edge={edge}
          tabIndex={peeking ? 0 : undefined}
          className="pdp-rail ky-gallery-port tab-scroll h-full"
          onKeyDown={onRailKeyDown}
          onScroll={onPortScroll}
        >
          {slides.map((slide, i) => {
            const isCenter = i === safeIndex;
            return (
              <div
                key={slide.id}
                ref={(node) => {
                  slideRefs.current[i] = node;
                }}
                className="pdp-slide ky-slide"
                role={peeking ? "group" : undefined}
                aria-roledescription={peeking ? "slide" : undefined}
                aria-label={peeking ? photoPositionLabel(i + 1, slideCount) : undefined}
              >
                <button
                  type="button"
                  data-testid={isCenter ? "gallery-open-lightbox" : undefined}
                  className="relative block h-full w-full cursor-zoom-in touch-manipulation"
                  aria-haspopup={isCenter || !peeking ? "dialog" : undefined}
                  onClick={() => {
                    if (isCenter || !peeking) {
                      onCenterClick?.();
                      return;
                    }
                    go(i);
                  }}
                  aria-label={
                    isCenter || !peeking
                      ? "Xem ảnh lớn · View larger"
                      : photoIndexLabel(i + 1)
                  }
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={slide.src}
                    alt={slide.alt}
                    draggable={false}
                    decoding={isCenter ? "sync" : "async"}
                    fetchPriority={isCenter ? "high" : "low"}
                    sizes={peeking ? "(min-width: 1024px) 42vw, 100vw" : "(min-width: 1024px) 50vw, 100vw"}
                    className="absolute inset-0 h-full w-full object-cover"
                  />
                </button>
              </div>
            );
          })}
        </div>

        {peeking ? <div aria-hidden className="gallery-water-sheen" /> : null}

        {peeking && !reduced ? (
          <motion.span
            aria-hidden
            className="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-px origin-left bg-gold"
            style={{ scaleX: scrollXProgress }}
          />
        ) : null}
      </div>

      {peeking ? (
        <div className="ky-gallery-dock pointer-events-auto absolute inset-x-0 top-[calc(100%+0.7rem)] z-20">
          <button
            type="button"
            onClick={() => go(safeIndex - 1)}
            disabled={!canPrev}
            aria-controls={railId}
            className="liquid-glass flex h-11 w-11 shrink-0 touch-manipulation items-center justify-center text-[15px] text-ink disabled:opacity-40"
            aria-label="Ảnh trước"
          >
            <span aria-hidden>←</span>
          </button>
          <div className="flex min-w-0 flex-1 justify-center gap-1">
            {slides.map((slide, i) => (
              <button
                key={`dot-${slide.id}`}
                type="button"
                aria-label={photoIndexLabel(i + 1)}
                aria-current={i === safeIndex}
                aria-controls={railId}
                aria-posinset={i + 1}
                aria-setsize={slideCount}
                onClick={() => go(i)}
                className="flex h-11 min-w-11 touch-manipulation items-center justify-center"
              >
                <span
                  className={`block rounded-full ${
                    i === safeIndex ? "h-2 w-7 bg-gold" : "h-2 w-2 bg-paper ring-1 ring-gold/55"
                  }`}
                  aria-hidden
                />
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={() => go(safeIndex + 1)}
            disabled={!canNext}
            aria-controls={railId}
            className="liquid-glass flex h-11 w-11 shrink-0 touch-manipulation items-center justify-center text-[15px] text-ink disabled:opacity-40"
            aria-label="Ảnh sau"
          >
            <span aria-hidden>→</span>
          </button>
        </div>
      ) : null}

      {center && slideCount > 0 ? (
        <p className="sr-only" aria-live="polite">
          {center.alt}
        </p>
      ) : null}
    </div>
  );
}
