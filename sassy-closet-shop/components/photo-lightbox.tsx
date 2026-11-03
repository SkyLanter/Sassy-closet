"use client";

import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState, useSyncExternalStore } from "react";
import { createPortal } from "react-dom";
import { motion, useReducedMotion } from "framer-motion";
import { FallibleLookPhoto } from "@/components/product-image";
import { ZoomLayer } from "@/components/zoom-layer";
import { cacheBustMediaSrc } from "@/lib/catalog-sha";
import {
  animateGalleryScrollTo,
  clampGalleryIndex,
  nearestStartIndex,
  scrollRailToChild,
} from "@/lib/gallery-snap";
import { photoIndexLabel, photoPositionLabel } from "@/lib/pdp-copy";
import type { ProductImageAsset } from "@/lib/types";

function GalleryNavButton({
  label,
  side,
  onClick,
  disabled,
  controlsId,
}: {
  label: string;
  side: "left" | "right";
  onClick: () => void;
  disabled: boolean;
  controlsId: string;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      aria-controls={controlsId}
      disabled={disabled}
      className="liquid-glass flex h-11 w-11 shrink-0 touch-manipulation items-center justify-center text-[15px] text-ink disabled:opacity-40"
      onClick={onClick}
    >
      <span aria-hidden>{side === "left" ? "←" : "→"}</span>
    </button>
  );
}

export function PhotoLightbox({
  title,
  ma,
  letter,
  colorLabel,
  slides,
  index,
  version,
  onClose,
  onIndex,
}: {
  title: string;
  ma: string;
  letter: string;
  colorLabel: string;
  slides: ProductImageAsset[];
  index: number;
  version: string;
  onClose: () => void;
  onIndex: (nextIndex: number) => void;
}) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const zoomOpenRef = useRef<HTMLButtonElement>(null);
  const zoomWasOpen = useRef(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const railRef = useRef<HTMLDivElement>(null);
  const slideRefs = useRef<Array<HTMLDivElement | null>>([]);
  const previousFocus = useRef<HTMLElement | null>(null);
  const indexRef = useRef(index);
  const onCloseRef = useRef(onClose);
  const onIndexRef = useRef(onIndex);
  const indexFromScroll = useRef(index);
  const jumpedToOpen = useRef(false);
  const ignoreScroll = useRef(false);
  const cancelRoll = useRef<(() => void) | null>(null);
  const titleId = useId();
  const railId = useId();
  const reduced = useReducedMotion();
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
  const safeIndex = clampGalleryIndex(index, slides.length);
  const current = slides[safeIndex];
  const src = current
    ? version
      ? cacheBustMediaSrc(current.src, version)
      : current.src
    : undefined;
  const zoomKey = `${safeIndex}:${src ?? ""}`;
  const [zoomFor, setZoomFor] = useState<string | null>(null);
  const zoomed = zoomFor === zoomKey;
  const peeking = slides.length > 1;

  useEffect(() => {
    if (zoomWasOpen.current && !zoomed) {
      zoomOpenRef.current?.focus({ preventScroll: true });
    }
    zoomWasOpen.current = zoomed;
  }, [zoomed]);

  const canPrev = peeking && safeIndex > 0;
  const canNext = peeking && safeIndex < slides.length - 1;

  const close = useCallback(() => {
    window.setTimeout(() => {
      onCloseRef.current();
    }, 0);
  }, []);

  const step = useCallback((delta: number) => {
    const next = clampGalleryIndex(indexRef.current + delta, slides.length);
    if (next !== indexRef.current) {
      onIndexRef.current(next);
    }
  }, [slides.length]);

  useEffect(() => {
    indexRef.current = safeIndex;
    onCloseRef.current = onClose;
    onIndexRef.current = onIndex;
  }, [onClose, onIndex, safeIndex]);

  useLayoutEffect(() => {
    const el = slideRefs.current[safeIndex];
    const port = railRef.current;
    if (!el || !port) {
      return;
    }
    if (jumpedToOpen.current && indexFromScroll.current === safeIndex) {
      return;
    }
    const firstOpen = !jumpedToOpen.current;
    jumpedToOpen.current = true;
    indexFromScroll.current = safeIndex;
    cancelRoll.current?.();
    if (firstOpen || reduced) {
      ignoreScroll.current = false;
      scrollRailToChild(port, el, "start");
      return;
    }
    ignoreScroll.current = true;
    cancelRoll.current = animateGalleryScrollTo(port, el, false, () => {
      ignoreScroll.current = false;
      cancelRoll.current = null;
    });
  }, [reduced, safeIndex, slides]);

  useLayoutEffect(() => {
    return () => {
      cancelRoll.current?.();
    };
  }, []);

  useEffect(() => {
    if (!mounted) {
      return;
    }
    previousFocus.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
    closeRef.current?.focus({ preventScroll: true });
    const overflow = document.body.style.overflow;
    const htmlOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
    function onKey(event: KeyboardEvent) {
      switch (event.key) {
        case "Escape":
          event.preventDefault();
          close();
          return;
        case "ArrowRight":
          event.preventDefault();
          step(1);
          return;
        case "ArrowLeft":
          event.preventDefault();
          step(-1);
          return;
        case "Home":
          event.preventDefault();
          onIndexRef.current(0);
          return;
        case "End":
          event.preventDefault();
          onIndexRef.current(slides.length - 1);
          return;
        case "Tab": {
          const root = dialogRef.current;
          if (!root) {
            return;
          }
          const focusable = [
            ...root.querySelectorAll<HTMLElement>("button, [href], input, textarea, select"),
          ].filter((node) => !node.hasAttribute("disabled") && node.tabIndex >= 0);
          if (focusable.length === 0) {
            return;
          }
          const first = focusable[0];
          const last = focusable[focusable.length - 1];
          const active = document.activeElement;
          if (event.shiftKey && active === first) {
            event.preventDefault();
            last?.focus();
          } else if (!event.shiftKey && active === last) {
            event.preventDefault();
            first?.focus();
          }
          return;
        }
        default:
          return;
      }
    }
    document.addEventListener("keydown", onKey);
    const keep = document.querySelector("[data-testid=\"gallery-lightbox\"]");
    const inerted: HTMLElement[] = [];
    if (keep) {
      for (const child of Array.from(document.body.children)) {
        if (!(child instanceof HTMLElement) || child === keep) {
          continue;
        }
        child.inert = true;
        inerted.push(child);
      }
    }
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = overflow;
      document.documentElement.style.overflow = htmlOverflow;
      for (const child of inerted) {
        child.inert = false;
      }
      previousFocus.current?.focus({ preventScroll: true });
    };
  }, [close, mounted, step]);

  const onRailScroll = () => {
    const port = railRef.current;
    if (!port || !peeking || ignoreScroll.current) {
      return;
    }
    const next = nearestStartIndex(port, slideRefs.current);
    if (next !== indexFromScroll.current) {
      indexFromScroll.current = next;
      onIndex(next);
    }
  };

  if (!mounted || !src) {
    return null;
  }

  return createPortal(
    <motion.div
      className="fixed inset-0 z-[80] flex items-center justify-center overscroll-contain"
      data-testid="gallery-lightbox"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={reduced ? { duration: 0 } : { duration: 0.18 }}
      style={{
        paddingTop: "max(1rem, env(safe-area-inset-top, 0px))",
        paddingBottom: "max(1rem, env(safe-area-inset-bottom, 0px))",
        paddingLeft: "max(1rem, env(safe-area-inset-left, 0px))",
        paddingRight: "max(1rem, env(safe-area-inset-right, 0px))",
      }}
    >
      <button
        type="button"
        aria-label="Đóng"
        tabIndex={-1}
        className="pdp-lightbox-veil absolute inset-0 bg-ink/70"
        onClick={close}
      />
      <motion.div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        initial={reduced ? false : { opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 6 }}
        transition={reduced ? { duration: 0 } : { duration: 0.2, ease: [0.23, 1, 0.32, 1] }}
        className="relative z-[1] flex max-h-full min-h-0 w-full max-w-3xl flex-col overflow-y-auto border border-gold bg-paper p-3 shadow-[0_18px_40px_-24px_rgba(17,17,17,0.45)] sm:p-4"
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <p id={titleId} className="line-clamp-3 font-display text-2xl leading-[1.08] tracking-[0.02em] text-balance text-ink" translate="no">
              {title}
            </p>
            <p
              className="mt-1 text-[11px] uppercase tracking-[0.16em] text-muted tabular-nums"
              aria-live="polite"
              aria-label={`${colorLabel}. ${photoPositionLabel(safeIndex + 1, slides.length)}`}
              translate="no"
            >
              {colorLabel} · {safeIndex + 1} / {slides.length}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <button
              ref={zoomOpenRef}
              type="button"
              data-testid="photo-zoom-open"
              onClick={() => setZoomFor(zoomKey)}
              className="sc-press inline-flex min-h-11 touch-manipulation items-center rounded-full border border-gold/45 px-4 text-[11px] uppercase tracking-[0.16em] text-ink"
              aria-label="Phóng to · Zoom"
            >
              Phóng to
            </button>
            <button
              ref={closeRef}
              type="button"
              onClick={close}
              aria-label="Đóng"
              className="flex h-11 w-11 touch-manipulation items-center justify-center rounded-full border border-gold/45 text-ink hover-hover:hover:border-gold"
            >
              <span aria-hidden>✕</span>
            </button>
          </div>
        </div>
        <div className="relative">
          <div
            ref={railRef}
            id={railId}
            data-testid="lightbox-rail"
            data-gallery-roll={peeking ? "peek" : "single"}
            className="pdp-lightbox-rail tab-scroll"
            onScroll={onRailScroll}
          >
            {slides.map((slideItem, slideIndex) => {
              const slideSrc = version
                ? cacheBustMediaSrc(slideItem.src, version)
                : slideItem.src;
              return (
                <div
                  key={`${slideItem.src}-${slideIndex}`}
                  ref={(node) => {
                    slideRefs.current[slideIndex] = node;
                  }}
                  className="pdp-slide"
                >
                  <div
                    className="pdp-lightbox-photo relative"
                    onDoubleClick={() => {
                      if (slideIndex === safeIndex) {
                        setZoomFor(zoomKey);
                      }
                    }}
                    onTouchStart={(event) => {
                      if (event.touches.length === 2 && slideIndex === safeIndex) {
                        setZoomFor(zoomKey);
                      }
                    }}
                  >
                    <FallibleLookPhoto
                      src={slideSrc}
                      alt={`${title}, ${colorLabel}, photo ${slideIndex + 1}`}
                      priority={slideIndex === safeIndex}
                      sizes="(min-width: 768px) 28rem, 100vw"
                      className="object-contain"
                      ma={ma}
                      letter={letter}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        {zoomed && src ? (
          <ZoomLayer
            src={src}
            alt={`${title}, ${colorLabel}`}
            ma={ma}
            letter={letter}
            onClose={() => setZoomFor(null)}
          />
        ) : null}
        {peeking ? (
          <div className="ky-gallery-dock mt-3 shrink-0">
            <GalleryNavButton
              label="Ảnh trước"
              side="left"
              disabled={!canPrev}
              controlsId={railId}
              onClick={() => step(-1)}
            />
            <div className="flex min-w-0 flex-1 justify-center gap-1">
              {slides.map((slideItem, slideIndex) => (
                <button
                  key={`dot-${slideItem.src}-${slideIndex}`}
                  type="button"
                  aria-label={photoIndexLabel(slideIndex + 1)}
                  aria-current={slideIndex === safeIndex}
                  aria-controls={railId}
                  onClick={() => onIndex(slideIndex)}
                  className="flex h-11 min-w-11 touch-manipulation items-center justify-center"
                >
                  <span
                    className={`block rounded-full ${
                      slideIndex === safeIndex ? "h-2 w-7 bg-gold" : "h-2 w-2 bg-paper ring-1 ring-gold/55"
                    }`}
                    aria-hidden
                  />
                </button>
              ))}
            </div>
            <GalleryNavButton
              label="Ảnh sau"
              side="right"
              disabled={!canNext}
              controlsId={railId}
              onClick={() => step(1)}
            />
          </div>
        ) : null}
        {peeking ? (
          <div className="ky-thumb-rail mt-3 flex shrink-0 flex-nowrap gap-2.5 overflow-x-auto tab-scroll">
            {slides.map((slideItem, slideIndex) => {
              const thumb = version ? cacheBustMediaSrc(slideItem.src, version) : slideItem.src;
              return (
                <button
                  key={`${slideItem.src}-${slideIndex}`}
                  type="button"
                  aria-label={photoIndexLabel(slideIndex + 1)}
                  aria-current={slideIndex === safeIndex}
                  aria-controls={railId}
                  onClick={() => onIndex(slideIndex)}
                  className={`ky-thumb-shot relative h-20 w-14 min-h-11 min-w-11 shrink-0 touch-manipulation overflow-hidden border ${
                    slideIndex === safeIndex ? "border-gold" : "border-gold/35 hover-hover:hover:border-gold"
                  }`}
                >
                  <FallibleLookPhoto
                    src={thumb}
                    alt=""
                    sizes="56px"
                    className="object-cover object-top"
                    ma={ma}
                    letter={letter}
                    compact
                  />
                </button>
              );
            })}
          </div>
        ) : null}
      </motion.div>
    </motion.div>,
    document.body,
  );
}
