"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { MessengerCta } from "@/components/messenger-cta";
import { useCategorySpy } from "@/components/category-spy";
import { categoryFilterLabel, categorySectionId } from "@/lib/categories";
import { LOOK_SEARCH_TOGGLE } from "@/lib/look-search";
import {
  editorialTitle,
  LOOK_STORY_EVENT,
  type LookStoryDetail,
} from "@/lib/look-story";
import { requestShopSearch } from "@/lib/open-shop-search";
import type { ShopLook } from "@/lib/shop-look";

type PillZone = "hidden" | "story" | "looks";

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

export function HomeFloatPill({ looks }: { looks: ShopLook[] }) {
  const first = looks[0];
  const { active } = useCategorySpy();
  const [zone, setZone] = useState<PillZone>("hidden");
  const [story, setStory] = useState<LookStoryDetail>(() => ({
    ma: first?.ma ?? "",
    title: first ? editorialTitle(first) : "",
    index: 0,
  }));

  useEffect(() => {
    const onStory = (event: Event) => {
      const detail = (event as CustomEvent<LookStoryDetail>).detail;
      if (!detail?.ma) {
        return;
      }
      setStory(detail);
    };
    window.addEventListener(LOOK_STORY_EVENT, onStory);
    return () => window.removeEventListener(LOOK_STORY_EVENT, onStory);
  }, []);

  useEffect(() => {
    let frame = 0;
    const update = () => {
      frame = 0;
      const chromeBottom =
        document.querySelector("[data-testid='shop-chrome']")?.getBoundingClientRect().bottom ?? 0;
      const storyRect = document.getElementById("look-story")?.getBoundingClientRect();
      const looksRect = document.getElementById("featured-collection")?.getBoundingClientRect();
      const view = window.innerHeight;
      const storyOn = Boolean(
        storyRect && storyRect.top < view * 0.78 && storyRect.bottom > chromeBottom + 48,
      );
      const looksOn = Boolean(
        looksRect && looksRect.top < view * 0.62 && looksRect.bottom > chromeBottom + 96,
      );
      let next: PillZone = "hidden";
      if (storyOn && (!looksOn || (storyRect?.top ?? 0) < view * 0.42)) {
        next = "story";
      } else if (looksOn) {
        next = "looks";
      } else if (storyOn) {
        next = "story";
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

  if (!first) {
    return null;
  }

  const open = zone !== "hidden";
  const category =
    active && active !== "all" ? categoryFilterLabel(active) : "Looks";
  const categoryHref =
    active && active !== "all" ? `#${categorySectionId(active)}` : "#featured-collection";
  const storyLook = looks.find((look) => look.ma === story.ma) ?? first;

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
        className="inline-flex h-11 w-11 shrink-0 touch-manipulation items-center justify-center rounded-full text-ink"
      >
        <SearchGlyph />
      </button>
      <div className="home-float-label min-w-0 flex-1">
        <PillLabel
          zone={zone}
          story={story}
          category={category}
          categoryHref={categoryHref}
        />
      </div>
      <MessengerCta
        ma={zone === "story" ? storyLook.ma : undefined}
        variant="header"
        className="shrink-0"
      />
    </div>
  );
}

function PillLabel({
  zone,
  story,
  category,
  categoryHref,
}: {
  zone: PillZone;
  story: LookStoryDetail;
  category: string;
  categoryHref: string;
}) {
  switch (zone) {
    case "hidden":
    case "story":
      return (
        <Link
          href={`/m/${story.ma}`}
          data-testid="home-float-story"
          translate="no"
          className="block min-h-11 truncate py-3 text-left text-[13px] leading-none text-ink"
        >
          <span className="text-gold-ink">{story.ma}</span>
          <span className="text-muted"> · </span>
          {story.title}
        </Link>
      );
    case "looks":
      return (
        <a
          href={categoryHref}
          data-testid="home-float-category"
          translate="no"
          className="block min-h-11 truncate py-3 text-left text-[13px] leading-none text-ink"
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
