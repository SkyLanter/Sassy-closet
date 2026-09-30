"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import Link from "next/link";
import { FallibleLookPhoto } from "@/components/product-image";
import { usePrefersReducedMotion } from "@/components/use-prefers-reduced-motion";
import { ProductPrice } from "@/components/product-price";
import { useCatalogMediaVersion } from "@/components/catalog-media-version";
import { categoryFilterLabel } from "@/lib/categories";
import { cacheBustMediaSrc } from "@/lib/catalog-sha";
import { coverSrc } from "@/lib/product-media";
import {
  editorialLine,
  editorialTitle,
  LOOK_STORY_EVENT,
  LOOK_STORY_SCROLL_OWN,
  lookStoryIndex,
  lookStoryProgress,
  type LookStoryDetail,
} from "@/lib/look-story";
import type { ShopLook } from "@/lib/shop-look";

const AUTOPLAY_MS = 6400;

function storySrc(look: ShopLook, version: string): string | undefined {
  const raw = coverSrc(look);
  if (!raw) {
    return undefined;
  }
  return version ? cacheBustMediaSrc(raw, version) : raw;
}

export function LookStory({ looks }: { looks: ShopLook[] }) {
  const version = useCatalogMediaVersion();
  const reduced = usePrefersReducedMotion();
  const sectionRef = useRef<HTMLElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const geom = useRef({ start: 0, travel: 1 });
  const progressRef = useRef(0);
  const scrollIndexRef = useRef(0);
  const scrollOwnedRef = useRef(false);
  const [scrollIndex, setScrollIndex] = useState(0);
  const [scrollOwned, setScrollOwned] = useState(false);
  const [floatIndex, setFloatIndex] = useState<number | null>(null);
  const [paused, setPaused] = useState(false);
  const [inView, setInView] = useState(false);
  const [pageHidden, setPageHidden] = useState(false);
  const count = looks.length;
  const autoplayHeld = paused || reduced === true;
  const activeIndex = scrollOwned ? scrollIndex : (floatIndex ?? 0);
  const active = looks[activeIndex] ?? looks[0];

  useEffect(() => {
    const section = sectionRef.current;
    const stage = stageRef.current;
    if (!section || !stage) {
      return;
    }
    let frame = 0;
    const measure = () => {
      frame = 0;
      const chrome = document.querySelector("[data-testid='shop-chrome']");
      const stickyTop = Math.ceil(chrome?.getBoundingClientRect().height ?? 0);
      section.style.setProperty("--look-sticky-top", `${stickyTop}px`);
      const sectionTop = section.getBoundingClientRect().top + window.scrollY;
      const start = sectionTop - stickyTop;
      const travel = Math.max(1, section.offsetHeight - stage.offsetHeight);
      geom.current = { start, travel };
      const progress = lookStoryProgress(window.scrollY - start, travel);
      progressRef.current = progress;
      const nextIndex = lookStoryIndex(progress, count);
      const owned = progress > LOOK_STORY_SCROLL_OWN;
      if (nextIndex !== scrollIndexRef.current) {
        scrollIndexRef.current = nextIndex;
        setScrollIndex(nextIndex);
      }
      if (owned !== scrollOwnedRef.current) {
        scrollOwnedRef.current = owned;
        setScrollOwned(owned);
        if (owned) {
          setFloatIndex(null);
        }
      }
    };
    const onScroll = () => {
      if (frame) {
        return;
      }
      frame = window.requestAnimationFrame(measure);
    };
    measure();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    const observer = new ResizeObserver(onScroll);
    observer.observe(section);
    const chrome = document.querySelector("[data-testid='shop-chrome']");
    if (chrome) {
      observer.observe(chrome);
    }
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      observer.disconnect();
      if (frame) {
        window.cancelAnimationFrame(frame);
      }
    };
  }, [count]);

  useEffect(() => {
    const stage = stageRef.current;
    if (!stage) {
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        setInView(entries.some((entry) => entry.isIntersecting && entry.intersectionRatio >= 0.45));
      },
      { threshold: [0, 0.45, 0.7] },
    );
    observer.observe(stage);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const onVis = () => setPageHidden(document.hidden);
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, []);

  useEffect(() => {
    if (reduced !== false || paused || scrollOwned || !inView || pageHidden || count < 2) {
      return;
    }
    const id = window.setInterval(() => {
      setFloatIndex((current) => ((current ?? 0) + 1) % count);
    }, AUTOPLAY_MS);
    return () => window.clearInterval(id);
  }, [count, inView, pageHidden, paused, reduced, scrollOwned]);

  useEffect(() => {
    const look = looks[activeIndex];
    if (!look) {
      return;
    }
    const detail: LookStoryDetail = {
      ma: look.ma,
      title: editorialTitle(look),
      index: activeIndex,
    };
    window.dispatchEvent(new CustomEvent(LOOK_STORY_EVENT, { detail }));
  }, [activeIndex, looks]);

  function scrollToLook(index: number) {
    const { start, travel } = geom.current;
    const progress = index <= 0 ? 0 : Math.min((index + 0.45) / count, 0.995);
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({
      top: start + progress * travel,
      behavior: reduce ? "auto" : "smooth",
    });
  }

  function goTo(index: number) {
    const next = ((index % count) + count) % count;
    setPaused(true);
    if (progressRef.current > LOOK_STORY_SCROLL_OWN) {
      scrollToLook(next);
      return;
    }
    setFloatIndex(next);
  }

  if (!active) {
    return null;
  }

  const title = editorialTitle(active);
  const line = editorialLine(active);

  return (
    <section
      id="look-story"
      ref={sectionRef}
      aria-labelledby="look-story-heading"
      data-testid="look-story"
      data-active-index={activeIndex}
      data-paused={paused ? "true" : "false"}
      className="look-story relative bg-paper"
      style={{ ["--look-steps" as string]: String(Math.max(count - 1, 1)) }}
    >
      <div ref={stageRef} className="look-story-stage ky-gutter" data-testid="look-story-stage">
        <div className="mx-auto grid w-full max-w-7xl items-center gap-5 md:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)] md:gap-14">
          <div className="order-1 min-w-0 md:order-2">
            <div
              role="region"
              aria-roledescription="carousel"
              aria-label="Popular looks"
              className="mx-auto w-full max-w-[17rem] md:max-w-[22rem]"
            >
              <Link
                href={`/m/${active.ma}`}
                aria-label={`${title}. ${active.ma}`}
                className="look-story-frame relative mx-auto block overflow-hidden rounded-[1.7rem] bg-[#f3f1ee] shadow-[0_24px_50px_-30px_rgb(176_112_98/0.55)]"
              >
                {looks.map((look, index) => {
                  const src = storySrc(look, version);
                  const on = index === activeIndex;
                  return (
                    <div
                      key={look.ma}
                      className="look-story-photo"
                      data-active={on ? "true" : "false"}
                      aria-hidden={on ? undefined : true}
                    >
                      {src ? (
                        <FallibleLookPhoto
                          src={src}
                          alt=""
                          sizes="(max-width: 768px) 70vw, 420px"
                          ma={look.ma}
                          letter={look.type}
                          className="object-contain object-center select-none"
                        />
                      ) : null}
                      <span className="liquid-glass-rim pointer-events-none absolute inset-0 z-[2]" aria-hidden />
                    </div>
                  );
                })}
              </Link>
              <div className="mt-4 flex items-center justify-center gap-2">
                <StoryControl
                  testId="look-story-prev"
                  label="Look trước · Previous look"
                  onClick={() => goTo(activeIndex - 1)}
                >
                  <Chevron direction="prev" />
                </StoryControl>
                <StoryControl
                  testId="look-story-pause"
                  label={autoplayHeld ? "Chạy · Play" : "Dừng · Pause"}
                  pressed={autoplayHeld}
                  onClick={() => setPaused((current) => !current)}
                >
                  {autoplayHeld ? <PlayIcon /> : <PauseIcon />}
                </StoryControl>
                <StoryControl
                  testId="look-story-next"
                  label="Look sau · Next look"
                  onClick={() => goTo(activeIndex + 1)}
                >
                  <Chevron direction="next" />
                </StoryControl>
              </div>
              <div className="flex items-center justify-center" role="tablist" aria-label="Popular looks">
                {looks.map((look, index) => {
                  const on = index === activeIndex;
                  return (
                    <button
                      key={look.ma}
                      type="button"
                      role="tab"
                      aria-selected={on}
                      aria-label={editorialTitle(look)}
                      data-testid="look-story-dot"
                      translate="no"
                      onClick={() => goTo(index)}
                      className="inline-flex h-11 w-8 touch-manipulation items-center justify-center"
                    >
                      <span
                        className={`block rounded-full motion-safe:transition-[width,background-color] motion-safe:duration-300 ${
                          on ? "h-1.5 w-5 bg-gold" : "h-1.5 w-1.5 bg-gold/40"
                        }`}
                      />
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
          <div className="order-2 min-w-0 md:order-1">
            <p
              className="text-[11px] font-medium uppercase tracking-[0.18em] text-muted"
              translate="no"
            >
              Popular
            </p>
            <span className="mt-3 block h-px w-10 bg-gold/70" aria-hidden />
            <div key={active.ma} className="look-story-copy">
              <h2
                id="look-story-heading"
                className="look-story-title mt-3 font-display text-[clamp(2rem,7vw,4.25rem)] font-medium leading-[0.98] tracking-[0.01em] text-balance text-ink"
                translate="no"
              >
                {title}
              </h2>
              <p
                className="look-story-line mt-3 max-w-md text-[15px] leading-[1.45] text-pretty text-muted"
                translate="no"
              >
                {line}
              </p>
              <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-1">
                <ProductPrice product={active} className="text-[15px] text-ink" />
                <Link
                  href={`/m/${active.ma}`}
                  data-testid="look-story-open"
                  translate="no"
                  className="inline-flex min-h-11 items-center text-[13px] text-gold-ink"
                >
                  Xem look · View look
                </Link>
              </div>
            </div>
            <p className="sr-only" aria-live="polite">
              {active.ma}. {title}. {categoryFilterLabel(active.type)}
            </p>
          </div>
        </div>
      </div>
      <div className="look-story-travel" aria-hidden />
    </section>
  );
}

function StoryControl({
  label,
  onClick,
  children,
  pressed,
  testId,
}: {
  label: string;
  onClick: () => void;
  children: ReactNode;
  pressed?: boolean;
  testId: string;
}) {
  return (
    <button
      type="button"
      data-testid={testId}
      aria-label={label}
      aria-pressed={pressed}
      translate="no"
      onClick={onClick}
      className="liquid-glass-chip inline-flex h-11 w-11 touch-manipulation items-center justify-center rounded-full text-ink"
    >
      {children}
    </button>
  );
}

function Chevron({ direction }: { direction: "prev" | "next" }) {
  const next = direction === "next";
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
        d={next ? "M9 6l6 6-6 6" : "M15 6l-6 6 6 6"}
      />
    </svg>
  );
}

function PauseIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden>
      <path fill="currentColor" d="M8 6h2.4v12H8V6Zm5.6 0H16v12h-2.4V6Z" />
    </svg>
  );
}

function PlayIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden>
      <path fill="currentColor" d="M8.2 5.8v12.4L18 12 8.2 5.8Z" />
    </svg>
  );
}
