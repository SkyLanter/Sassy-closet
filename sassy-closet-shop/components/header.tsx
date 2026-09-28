"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { HScrollCue } from "@/components/h-scroll-cue";
import { HeaderSearch, HeaderSearchProvider, HeaderSearchSheet } from "@/components/header-search";
import { MessengerCta } from "@/components/messenger-cta";
import { onShopHomeClick, useShopSearch } from "@/components/shop-search";
import { categoryAriaLabel, categoryCopy, categoryHref } from "@/lib/categories";
import { scrollChromeChildIntoView } from "@/lib/gallery-snap";
import type { MaLetter } from "@/lib/ma";
import { easeOutFast } from "@/lib/motion";
import { SITE } from "@/lib/site";

export function Header({ types }: { types: MaLetter[] }) {
  const pathname = usePathname();
  const { clearSearch } = useShopSearch();
  const reduced = useReducedMotion();
  const navRef = useRef<HTMLElement | null>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 4);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useLayoutEffect(() => {
    scrollChromeChildIntoView(
      navRef.current,
      navRef.current?.querySelector<HTMLElement>('[aria-current="page"]') ?? null,
    );
  }, [pathname]);

  return (
    <HeaderSearchProvider types={types} onExpandedChange={setSearchOpen}>
    <motion.header
      className="ky-header-film liquid-glass-bar relative"
      data-scrolled={scrolled ? "true" : "false"}
      style={{ viewTransitionName: "site-header" }}
    >
      <div className="ky-header-row relative z-20 mx-auto flex h-14 min-w-0 max-w-7xl items-center justify-between gap-2 pl-[max(1.25rem,env(safe-area-inset-left,0px))] pr-[max(1.25rem,env(safe-area-inset-right,0px))] sm:h-16 sm:gap-3 sm:pl-[max(2rem,env(safe-area-inset-left,0px))] sm:pr-[max(2rem,env(safe-area-inset-right,0px))]">
        <Link
          href="/"
          data-testid="shop-logo"
          aria-current={pathname === "/" ? "page" : undefined}
          translate="no"
          className={`ky-header-wordmark inline-flex min-h-11 min-w-0 touch-manipulation select-none items-center truncate whitespace-nowrap font-display text-[1.65rem] font-medium leading-[1.12] tracking-[0.02em] text-balance text-ink hover-hover:hover:text-gold-ink ${
            searchOpen ? "max-sm:hidden" : ""
          }`}
          onClick={(event) => {
            onShopHomeClick(event, clearSearch);
          }}
        >
          {SITE.name}
        </Link>
        <div
          className={`flex min-w-0 items-center justify-end gap-2 sm:gap-3 ${
            searchOpen ? "flex-1" : "shrink-0"
          }`}
        >
          <HeaderSearch />
          <MessengerCta variant="header" className="shrink-0" />
        </div>
      </div>
      <HScrollCue className="ky-h-scroll-cue min-w-0">
      <LayoutGroup>
        <motion.nav
          ref={navRef}
          layoutScroll
          className="relative flex h-11 min-w-0 max-w-full items-end justify-start gap-6 overflow-x-auto ky-split-hairline pb-1 tab-scroll scroll-pl-[max(1.25rem,env(safe-area-inset-left,0px))] scroll-pr-[max(1.25rem,env(safe-area-inset-right,0px))] pl-[max(1.25rem,env(safe-area-inset-left,0px))] pr-[max(1.25rem,env(safe-area-inset-right,0px))] sm:gap-10 sm:pl-[max(2rem,env(safe-area-inset-left,0px))] sm:pr-[max(2rem,env(safe-area-inset-right,0px))] sm:scroll-pl-[max(2rem,env(safe-area-inset-left,0px))] sm:scroll-pr-[max(2rem,env(safe-area-inset-right,0px))]"
          aria-label="Danh mục · Categories"
        >
          {types.map((type) => {
            const href = categoryHref(type);
            const active = pathname === href || pathname.startsWith(`${href}/`);
            const labels = categoryCopy(type);
            return (
              <Link
                key={type}
                href={href}
                aria-current={active ? "page" : undefined}
                aria-label={categoryAriaLabel(type)}
                translate="no"
                className={`relative inline-flex min-h-11 min-w-11 shrink-0 touch-manipulation select-none items-end justify-center whitespace-nowrap pb-1.5 text-[11px] font-medium uppercase tracking-[0.16em] ${
                  active ? "text-ink" : "text-muted hover-hover:hover:text-ink"
                }`}
              >
                {labels.label}
                {active ? (
                  <motion.span
                    layoutId={reduced ? undefined : "nav-tab"}
                    className="absolute inset-x-0 bottom-0 h-px bg-gold"
                    initial={false}
                    transition={reduced ? { duration: 0 } : easeOutFast}
                    aria-hidden
                  />
                ) : null}
              </Link>
            );
          })}
        </motion.nav>
      </LayoutGroup>
      </HScrollCue>
      </motion.header>
    <HeaderSearchSheet />
    </HeaderSearchProvider>
  );
}
