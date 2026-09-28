"use client";

import { MessengerCta } from "@/components/messenger-cta";
import { SHOP_ERROR_BODY } from "@/lib/pdp-copy";

export default function ShopError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="mx-auto max-w-xl ky-gutter py-24 text-center" role="alert" data-testid="shop-error">
      <p className="font-display text-[2.35rem] font-medium leading-[1.08] tracking-[0.03em] text-balance text-ink sm:text-5xl" translate="no">
        Không tải được looks · Could not load looks
      </p>
      <p className="mt-3 text-pretty text-sm text-muted" translate="no">{SHOP_ERROR_BODY}</p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
        <button
          type="button"
          onClick={reset}
          aria-label="Thử lại · Try again"
          translate="no"
          className="sc-press inline-flex min-h-11 touch-manipulation select-none items-center rounded-full border border-gold/45 px-4 text-[11px] uppercase tracking-[0.16em] text-ink hover-hover:hover:border-gold"
        >
          Try again
        </button>
        <MessengerCta />
      </div>
    </div>
  );
}
