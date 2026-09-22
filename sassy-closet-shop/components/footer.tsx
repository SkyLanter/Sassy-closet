"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessengerCta } from "@/components/messenger-cta";
import { SITE } from "@/lib/site";

export function Footer() {
  const pathname = usePathname();
  const aboveBuyBar = pathname.startsWith("/m/");

  return (
    <footer
      className={`ky-footer-film mt-auto bg-paper ${
        aboveBuyBar ? "md:pb-[max(2rem,env(safe-area-inset-bottom,0px))]" : "pb-[max(2rem,env(safe-area-inset-bottom,0px))]"
      }`}
    >
      <div className="mx-auto flex max-w-7xl flex-col gap-4 pt-10 sm:pt-12 pl-[max(1.25rem,env(safe-area-inset-left,0px))] pr-[max(1.25rem,env(safe-area-inset-right,0px))] sm:flex-row sm:items-center sm:justify-between sm:pl-[max(2rem,env(safe-area-inset-left,0px))] sm:pr-[max(2rem,env(safe-area-inset-right,0px))]">
        <Link
          href="/"
          aria-current={pathname === "/" ? "page" : undefined}
          translate="no"
          className="inline-flex min-h-11 max-w-full touch-manipulation select-none items-center truncate whitespace-nowrap font-display text-lg leading-[1.12] tracking-[0.02em] text-balance text-ink hover-hover:hover:text-gold-deep"
        >
          {SITE.name}
        </Link>
        <MessengerCta variant="ghost" />
      </div>
      {aboveBuyBar ? (
        <div
          aria-hidden
          data-testid="shop-buy-bar-spacer"
          className="pointer-events-none md:hidden"
          style={{ height: "var(--shop-buy-bar-space)" }}
        />
      ) : null}
    </footer>
  );
}
