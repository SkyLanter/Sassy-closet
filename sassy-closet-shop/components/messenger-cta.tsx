"use client";

import { useEffect, useState } from "react";
import { MaMark } from "@/components/ma-mark";
import { useMessengerAppDevice } from "@/components/messenger-device";
import { useSiteSettings } from "@/components/site-settings";
import { useCanHover } from "@/lib/hover";
import {
  messengerHref,
  messengerTapHref,
  messengerUsesAppScheme,
} from "@/lib/messenger";
import { messageAria } from "@/lib/pdp-copy";
import { SITE } from "@/lib/site";

type MessengerVariant = "primary" | "header" | "ghost" | "card";

type MessengerCtaProps = {
  ma?: string;
  askPrice?: boolean;
  variant?: MessengerVariant;
  className?: string;
};

function classNames(...parts: Array<string | false | undefined>): string {
  return parts.filter(Boolean).join(" ");
}

function MessengerGlyph() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" aria-hidden>
      <path
        fill="currentColor"
        d="M12 3.2C6.9 3.2 2.8 6.9 2.8 11.4c0 2.6 1.3 4.9 3.4 6.4v3l3.1-1.7c.9.2 1.8.4 2.7.4 5.1 0 9.2-3.7 9.2-8.1S17.1 3.2 12 3.2Zm.9 10.3-2.4-2.5-4.6 2.5 5.1-5.4 2.4 2.5 4.6-2.5-5.1 5.4Z"
      />
    </svg>
  );
}

function variantStyles(variant: MessengerVariant): string {
  switch (variant) {
    case "primary":
      return "min-h-11 bg-ink px-5 py-2.5 text-sm text-paper shadow-sm motion-safe:transition-all motion-safe:duration-300 hover-hover:hover:-translate-y-0.5 hover-hover:hover:shadow-[0_8px_20px_-14px_rgba(17,17,17,0.5)]";
    case "header":
      return "min-h-11 px-0 py-0 text-[11px] uppercase tracking-[0.18em] text-ink";
    case "ghost":
      return "min-h-11 border border-gold/45 px-4 py-1.5 text-xs text-ink hover-hover:hover:border-gold";
    case "card":
      return "min-h-11 px-0 py-0 text-[11px] uppercase tracking-[0.16em] text-ink hover-hover:hover:text-gold-deep";
    default: {
      const _exhaustive: never = variant;
      return _exhaustive;
    }
  }
}

/**
 * Message-to-buy CTA. Always a native <a href> — never a click handler, timer,
 * or motion wrapper (those break the Messenger app hop on phones).
 * Phone taps the fb-messenger:// app scheme; desktop stays on https://m.me.
 * Phones without the app installed get a separate "Open on web" m.me link.
 */
export function MessengerCta({
  ma,
  askPrice = false,
  variant = "primary",
  className,
}: MessengerCtaProps) {
  const canHover = useCanHover();
  const isAppDevice = useMessengerAppDevice();
  const { facebookPageUrl } = useSiteSettings();
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const webHref = messengerHref(facebookPageUrl);
  const useAppScheme = messengerUsesAppScheme(isAppDevice, canHover);
  const tapHref = messengerTapHref(facebookPageUrl, useAppScheme);
  // Server + hydration markup must match: before mount, only UA-flagged app
  // devices render the web fallback. After mount the real tap href decides.
  const showWebFallback =
    webHref !== "" &&
    tapHref !== "" &&
    tapHref !== webHref &&
    (mounted || isAppDevice);

  const label = ma
    ? undefined
    : variant === "header"
      ? "Messenger"
      : SITE.messengerCtaLabel;

  const ariaLabel = messageAria(ma);
  const isHeader = variant === "header";
  const isCard = variant === "card";
  const showChromeRim = !isHeader && !isCard;

  const anchor = (
    <a
      href={tapHref || undefined}
      target="_blank"
      rel="noopener noreferrer"
      referrerPolicy="no-referrer"
      aria-label={ariaLabel}
      data-testid={askPrice ? "shop-ask-price" : "shop-message-cta"}
      data-messenger-ref={ma ?? undefined}
      data-messenger-scheme={useAppScheme ? "app" : "web-newtab"}
      translate="no"
      className={classNames(
        "group/cta relative inline-flex touch-manipulation select-none items-center justify-center gap-2 whitespace-nowrap font-medium",
        isHeader || isCard ? "" : "cta-shine overflow-hidden rounded-full",
        variantStyles(variant),
        className,
      )}
    >
      {showChromeRim ? <span className="ky-chrome-rim" aria-hidden /> : null}
      <span className="relative z-[1] inline-flex items-center justify-center gap-2">
        {variant === "primary" ? <MessengerGlyph /> : null}
        {ma ? (
          askPrice ? (
            <>
              <span>Hỏi giá · Ask price</span>
              <MaMark ma={ma} className="text-[1em] tracking-[0.1em]" />
            </>
          ) : (
            <>
              Message <MaMark ma={ma} className="text-[1em] tracking-[0.1em]" />
            </>
          )
        ) : (
          label
        )}
        {isHeader || isCard ? null : (
          <span aria-hidden className="text-[0.95em]">
            →
          </span>
        )}
      </span>
      {isHeader || isCard ? (
        <span className="absolute bottom-0 left-0 h-px w-full bg-gold/45" aria-hidden />
      ) : null}
    </a>
  );

  if (variant !== "primary" || !showWebFallback) {
    return anchor;
  }

  return (
    <span className="inline-flex min-w-0 shrink-0 flex-col items-stretch gap-1">
      {anchor}
      <a
        href={webHref}
        target="_blank"
        rel="noopener noreferrer"
        referrerPolicy="no-referrer"
        data-testid="shop-message-web"
        aria-label="Mở trên web · Open on web"
        translate="no"
        className="inline-flex min-h-11 touch-manipulation select-none items-center justify-center whitespace-nowrap text-[11px] uppercase tracking-[0.16em] text-muted underline decoration-gold/50 underline-offset-4 hover-hover:hover:text-ink"
      >
        Open on web
      </a>
    </span>
  );
}
