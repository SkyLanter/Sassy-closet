"use client";

import { useEffect, useState } from "react";
import { MessengerCta } from "@/components/messenger-cta";
import { useCategorySpy } from "@/components/category-spy";
import { categoryFilterLabel, categorySectionId } from "@/lib/categories";
import { LOOK_SEARCH_TOGGLE } from "@/lib/look-search";
import { requestShopSearch } from "@/lib/open-shop-search";

type PillZone = "hidden" | "cards" | "looks";

function SearchGlyph() {
  return (
    <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" aria-hidden>
      <path
        fill="currentColor"
        d="M10.5 3.8a6.7 6.7 0 0 1 5.2 10.9l4 4a.9.9 0 0 1-1.3 1.3l-4-4A6.7 6.7 0 1 1 10.5 3.8Zm0 1.7a5 5 0 1 0 0 10 5 5 0 0 0 0-10Z"
      />
    </svg>
  );
}

export function HomeFloatPill() {
  const { active } = useCategorySpy();
  const [zone, setZone] = useState<PillZone>("hidden");

  useEffect(() => {
    let frame = 0;
    const update = () => {
      frame = 0;
      const chromeBottom =
        document.querySelector("[data-testid='shop-chrome']")?.getBoundingClientRect().bottom ?? 0;
      const cards = document.querySelector("[data-testid='home-feature-cards']")?.getBoundingClientRect();
      const looks = document.getElementById("featured-collection")?.getBoundingClientRect();
      const view = window.innerHeight;
      const cardsOn = Boolean(cards && cards.top < view * 0.82 && cards.bottom > chromeBottom + 32);
      const looksOn = Boolean(looks && looks.top < view * 0.62 && looks.bottom > chromeBottom + 80);
      let next: PillZone = "hidden";
      if (window.scrollY < 64) {
        next = "hidden";
      } else if (looksOn && (looks?.top ?? view) < view * 0.42) {
        next = "looks";
      } else if (cardsOn) {
        next = "cards";
      } else if (looksOn) {
        next = "looks";
      }
      setZone((current) => (current === next ? current : next));
    };
    const onScroll = () => {
      if (frame) {
        return;
      }
      frame = window.requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (frame) {
        window.cancelAnimationFrame(frame);
      }
    };
  }, []);

  const open = zone !== "hidden";
  const category = active && active !== "all" ? categoryFilterLabel(active) : "Looks";
  const categoryHref =
    active && active !== "all" ? `#${categorySectionId(active)}` : "#featured-collection";

  return (
    <div
      data-testid="home-float-pill"
      data-open={open ? "true" : "false"}
      data-zone={zone}
      inert={open ? undefined : true}
      className="home-float-pill"
    >
      <button
        type="button"
        data-testid="home-float-search"
        aria-label={LOOK_SEARCH_TOGGLE}
        translate="no"
        onClick={() => requestShopSearch()}
        className="home-float-search inline-flex h-11 w-11 shrink-0 touch-manipulation items-center justify-center rounded-full text-ink"
      >
        <SearchGlyph />
      </button>
      <div className="min-w-0 flex-1">
        <PillLabel zone={zone} category={category} categoryHref={categoryHref} />
      </div>
      <MessengerCta variant="header" className="shrink-0" />
    </div>
  );
}

function PillLabel({
  zone,
  category,
  categoryHref,
}: {
  zone: PillZone;
  category: string;
  categoryHref: string;
}) {
  switch (zone) {
    case "hidden":
    case "cards":
      return (
        <a
          href="#home-categories-heading"
          data-testid="home-float-category"
          translate="no"
          className="block min-h-11 truncate py-3 text-left text-[13px] leading-none tracking-[0.01em] text-ink"
        >
          Categories
        </a>
      );
    case "looks":
      return (
        <a
          href={categoryHref}
          data-testid="home-float-category"
          translate="no"
          className="block min-h-11 truncate py-3 text-left text-[13px] leading-none tracking-[0.01em] text-ink"
        >
          {category}
        </a>
      );
    default: {
      const _exhaustive: never = zone;
      return _exhaustive;
    }
  }
}
