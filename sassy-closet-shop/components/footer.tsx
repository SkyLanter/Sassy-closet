"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessengerCta } from "@/components/messenger-cta";
import { SITE } from "@/lib/site";

/** IG handle from the shop's standing records — not in code, so kept as a plain constant. */
const INSTAGRAM_URL = "https://www.instagram.com/sassycloset.boutique";

function SocialGlyph({ label }: { label: "facebook" | "instagram" }) {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" aria-hidden>
      {label === "facebook" ? (
        <path
          fill="currentColor"
          d="M13.5 21v-7h2.4l.4-3h-2.8V9.1c0-.9.3-1.5 1.6-1.5h1.3V4.9c-.3 0-1.1-.1-2-.1-2 0-3.4 1.2-3.4 3.5V11H8.5v3H11v7h2.5Z"
        />
      ) : (
        <path
          fill="currentColor"
          d="M12 4.5c-2.5 0-2.8 0-3.8.1-1 .1-1.7.2-2.3.5-.6.2-1.1.6-1.6 1-.4.5-.8 1-1 1.6-.3.6-.4 1.3-.5 2.3-.1 1-.1 1.3-.1 3.8s0 2.8.1 3.8c.1 1 .2 1.7.5 2.3.2.6.6 1.1 1 1.6.5.4 1 .8 1.6 1 .6.3 1.3.4 2.3.5 1 .1 1.3.1 3.8.1s2.8 0 3.8-.1c1-.1 1.7-.2 2.3-.5.6-.2 1.1-.6 1.6-1 .4-.5.8-1 1-1.6.3-.6.4-1.3.5-2.3.1-1 .1-1.3.1-3.8s0-2.8-.1-3.8c-.1-1-.2-1.7-.5-2.3-.2-.6-.6-1.1-1-1.6-.5-.4-1-.8-1.6-1-.6-.3-1.3-.4-2.3-.5-1-.1-1.3-.1-3.8-.1Zm0 1.7c2.4 0 2.7 0 3.7.1.9 0 1.4.2 1.7.3.4.2.7.4 1 .7.3.3.5.6.7 1 .1.3.3.8.3 1.7.1 1 .1 1.3.1 3.7s0 2.7-.1 3.7c0 .9-.2 1.4-.3 1.7-.2.4-.4.7-.7 1-.3.3-.6.5-1 .7-.3.1-.8.3-1.7.3-1 .1-1.3.1-3.7.1s-2.7 0-3.7-.1c-.9 0-1.4-.2-1.7-.3-.4-.2-.7-.4-1-.7-.3-.3-.5-.6-.7-1-.1-.3-.3-.8-.3-1.7-.1-1-.1-1.3-.1-3.7s0-2.7.1-3.7c0-.9.2-1.4.3-1.7.2-.4.4-.7.7-1 .3-.3.6-.5 1-.7.3-.1.8-.3 1.7-.3 1-.1 1.3-.1 3.7-.1Zm0 2.9a4.9 4.9 0 1 0 0 9.8 4.9 4.9 0 0 0 0-9.8Zm0 8.1a3.2 3.2 0 1 1 0-6.4 3.2 3.2 0 0 1 0 6.4Zm6.3-8.3a1.1 1.1 0 1 1-2.3 0 1.1 1.1 0 0 1 2.3 0Z"
        />
      )}
    </svg>
  );
}

export function Footer() {
  const pathname = usePathname();
  const aboveBuyBar = pathname.startsWith("/m/");
  const year = new Date().getFullYear();

  return (
    <footer
      className={`ky-footer-film mt-auto bg-paper ${
        aboveBuyBar ? "md:pb-[max(2rem,env(safe-area-inset-bottom,0px))]" : "pb-[max(2rem,env(safe-area-inset-bottom,0px))]"
      }`}
    >
      <div className="mx-auto flex max-w-7xl flex-col gap-4 pt-10 sm:pt-12 pl-[max(1.25rem,env(safe-area-inset-left,0px))] pr-[max(1.25rem,env(safe-area-inset-right,0px))] sm:flex-row sm:items-center sm:justify-between sm:pl-[max(2rem,env(safe-area-inset-left,0px))] sm:pr-[max(2rem,env(safe-area-inset-right,0px))]">
        <div className="min-w-0">
          <Link
            href="/"
            aria-current={pathname === "/" ? "page" : undefined}
            translate="no"
            className="inline-flex min-h-11 max-w-full touch-manipulation select-none items-center truncate whitespace-nowrap font-display text-lg leading-[1.12] tracking-[0.02em] text-balance text-ink hover-hover:hover:text-gold-deep"
          >
            {SITE.name}
          </Link>
          <p className="mt-1 text-[13px] leading-relaxed text-muted" translate="no">
            Nhắn tin để mua · Message to buy on Messenger
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
          <nav aria-label="Liên hệ · Contact" className="flex flex-wrap items-center gap-x-1">
            <a
              href={SITE.facebookPageUrl}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Sassy Closet trên Facebook · Sassy Closet on Facebook"
              className="inline-flex min-h-11 min-w-11 touch-manipulation items-center justify-center gap-2 rounded-full px-3 text-[11px] font-medium uppercase tracking-[0.16em] text-muted hover-hover:hover:text-ink"
            >
              <SocialGlyph label="facebook" />
              Facebook
            </a>
            <a
              href={INSTAGRAM_URL}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Sassy Closet trên Instagram · Sassy Closet on Instagram"
              className="inline-flex min-h-11 min-w-11 touch-manipulation items-center justify-center gap-2 rounded-full px-3 text-[11px] font-medium uppercase tracking-[0.16em] text-muted hover-hover:hover:text-ink"
            >
              <SocialGlyph label="instagram" />
              Instagram
            </a>
          </nav>
          <MessengerCta variant="ghost" />
        </div>
      </div>
      <div className="mx-auto max-w-7xl pt-6 pl-[max(1.25rem,env(safe-area-inset-left,0px))] pr-[max(1.25rem,env(safe-area-inset-right,0px))] sm:pl-[max(2rem,env(safe-area-inset-left,0px))] sm:pr-[max(2rem,env(safe-area-inset-right,0px))]">
        <p className="border-t border-ink/10 pt-4 text-[11px] uppercase tracking-[0.16em] text-muted" translate="no">
          © {year} Sassy Closet
        </p>
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
