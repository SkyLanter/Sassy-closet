"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGroup, motion, useReducedMotion } from "framer-motion";
import { useAdminEntry } from "@/components/admin-entry";
import { HeaderSearch, HeaderSearchProvider, HeaderSearchSheet } from "@/components/header-search";
import { MessengerCta } from "@/components/messenger-cta";
import { categoryAriaLabel, categoryCopy, categoryHref } from "@/lib/categories";
import { scrollChromeChildIntoView } from "@/lib/gallery-snap";
import type { MaLetter } from "@/lib/ma";
import { springSoft } from "@/lib/motion";
import { SITE } from "@/lib/site";

export function Header({ types }: { types: MaLetter[] }) {
  const pathname = usePathname();
  const reduced = useReducedMotion();
  const studio = useAdminEntry();
  const holdTimer = useRef<number | null>(null);
  const gated = useRef(false);
  const navRef = useRef<HTMLElement | null>(null);
  const [searchOpen, setSearchOpen] = useState(false);

  useLayoutEffect(() => {
    scrollChromeChildIntoView(
      navRef.current,
      navRef.current?.querySelector<HTMLElement>('[aria-current="page"]') ?? null,
    );
  }, [pathname]);

  useEffect(() => {
    return () => {
      if (holdTimer.current !== null) {
        window.clearTimeout(holdTimer.current);
      }
    };
  }, []);

  function clearHold() {
    if (holdTimer.current !== null) {
      window.clearTimeout(holdTimer.current);
      holdTimer.current = null;
    }
  }

  function startHold() {
    clearHold();
    gated.current = false;
    holdTimer.current = window.setTimeout(() => {
      gated.current = true;
      studio?.openStudio();
    }, 700);
  }

  return (
    <HeaderSearchProvider onExpandedChange={setSearchOpen}>
    <motion.header
      className="ky-header-film liquid-glass-bar relative"
      style={{ viewTransitionName: "site-header" }}
    >
      <div className="relative z-20 mx-auto flex h-14 min-w-0 max-w-7xl items-center justify-between gap-2 pl-[max(1.25rem,env(safe-area-inset-left,0px))] pr-[max(1.25rem,env(safe-area-inset-right,0px))] sm:h-16 sm:gap-3 sm:pl-[max(2rem,env(safe-area-inset-left,0px))] sm:pr-[max(2rem,env(safe-area-inset-right,0px))]">
        <Link
          href="/"
          aria-current={pathname === "/" ? "page" : undefined}
          translate="no"
          className={`inline-flex min-h-11 min-w-0 touch-manipulation select-none items-center truncate whitespace-nowrap font-display text-[1.65rem] font-medium leading-[1.12] tracking-[0.02em] text-balance text-ink hover-hover:hover:text-gold-deep ${
            searchOpen ? "max-sm:hidden" : ""
          }`}
          onPointerDown={startHold}
          onPointerUp={clearHold}
          onPointerCancel={clearHold}
          onPointerLeave={clearHold}
          onClick={(event) => {
            if (gated.current) {
              event.preventDefault();
              gated.current = false;
            }
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
      <div className="ky-h-scroll-cue">
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
                className={`relative inline-flex min-h-11 shrink-0 touch-manipulation select-none items-end whitespace-nowrap pb-1.5 text-[11px] font-medium uppercase tracking-[0.16em] ${
                  active ? "text-ink" : "text-muted hover-hover:hover:text-ink"
                }`}
              >
                {labels.label}
                {active ? (
                  <motion.span
                    layoutId={reduced ? undefined : "nav-tab"}
                    className="absolute inset-x-0 bottom-0 h-px bg-gold"
                    initial={false}
                    transition={reduced ? { duration: 0 } : springSoft}
                    aria-hidden
                  />
                ) : null}
              </Link>
            );
          })}
        </motion.nav>
      </LayoutGroup>
      </div>
    </motion.header>
    <HeaderSearchSheet />
    </HeaderSearchProvider>
  );
}
