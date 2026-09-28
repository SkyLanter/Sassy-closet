"use client";

import { track } from "@vercel/analytics";
import { motion, useReducedMotion } from "framer-motion";
import { MaMark } from "@/components/ma-mark";
import { useSiteSettings } from "@/components/site-settings";
import { useCanHover } from "@/lib/hover";
import { messengerAskHref } from "@/lib/messenger-ask";
import { messengerHref } from "@/lib/messenger";
import { messageAria } from "@/lib/pdp-copy";
import { SITE } from "@/lib/site";

type MessengerVariant = "primary" | "header" | "ghost" | "card";

type MessengerCtaProps = {
  ma?: string;
  sizeLabel?: string | null;
  colorLabel?: string | null;
  askPrice?: boolean;
  variant?: MessengerVariant;
  className?: string;
};

function classNames(...parts: Array<string | false | undefined>): string {
  return parts.filter(Boolean).join(" ");
}

function MessengerGlyph() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4 shrink-0" aria-hidden>
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
      return "min-h-11 px-5 py-2.5 text-sm text-ink";
    case "header":
      return "min-h-11 px-3 py-0 text-[11px] uppercase tracking-[0.18em] text-ink";
    case "ghost":
      return "min-h-11 border border-gold/45 px-4 py-1.5 text-xs text-ink hover-hover:hover:border-gold";
    case "card":
      return "sc-card-message min-h-11 px-3 py-0 text-[11px] uppercase tracking-[0.16em] text-ink hover-hover:hover:text-gold-ink";
    default: {
      const _exhaustive: never = variant;
      return _exhaustive;
    }
  }
}

export function MessengerCta({
  ma,
  sizeLabel = null,
  colorLabel = null,
  askPrice = false,
  variant = "primary",
  className,
}: MessengerCtaProps) {
  const reduced = useReducedMotion();
  const canHover = useCanHover();
  const { facebookPageUrl } = useSiteSettings();
  const href = ma
    ? messengerAskHref(facebookPageUrl, ma, sizeLabel, colorLabel)
    : messengerHref(facebookPageUrl);
  const label = ma
    ? `Message ${ma}`
    : variant === "header"
      ? "Messenger"
      : SITE.messengerCtaLabel;

  const ariaLabel = messageAria(ma);
  const isHeader = variant === "header";
  const isCard = variant === "card";
  const showChromeRim = !isHeader && !isCard;

  function onMessengerClick() {
    if (!ma) {
      return;
    }
    track("messenger_cta", { ma });
  }

  return (
    <motion.a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      referrerPolicy="no-referrer"
      onClick={onMessengerClick}
      aria-label={ariaLabel}
      data-testid={askPrice ? "shop-ask-price" : "shop-message-cta"}
      data-messenger-ref={ma ?? undefined}
      data-messenger-scheme="web-newtab"
      translate="no"
      whileHover={
        reduced || isHeader || isCard || !canHover ? undefined : { y: -2 }
      }
      whileTap={reduced || isHeader || isCard ? undefined : { scale: 0.97 }}
      transition={{ type: "spring", stiffness: 520, damping: 28 }}
      className={classNames(
        "group/cta sc-messenger-glass sc-press sc-glass-cta liquid-glass-chip relative inline-flex touch-manipulation select-none items-center justify-center gap-2 overflow-hidden whitespace-nowrap rounded-full font-medium",
        variantStyles(variant),
        className,
      )}
    >
      {showChromeRim ? <span className="ky-chrome-rim" aria-hidden /> : null}
      <span className="relative z-[2] inline-flex items-center justify-center gap-2">
        {variant === "primary" ? <MessengerGlyph /> : null}
        {ma ? (
          <>
            Message <MaMark ma={ma} className="text-[1em] tracking-[0.1em]" />
          </>
        ) : (
          label
        )}
        {isHeader || isCard ? null : (
          <span
            aria-hidden
            className="text-[0.95em] motion-safe:transition-transform motion-safe:duration-300 motion-safe:hover-hover:group-hover/cta:translate-x-0.5"
          >
            →
          </span>
        )}
      </span>
      {isHeader ? (
        <span className="absolute bottom-0 left-0 h-px w-full bg-gold/45" aria-hidden />
      ) : null}
    </motion.a>
  );
}
