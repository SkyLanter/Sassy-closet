"use client";

import { MaMark } from "@/components/ma-mark";
import { MessengerCta } from "@/components/messenger-cta";
import { ProductPrice } from "@/components/product-price";
import { displayName } from "@/lib/copy";
import type { ShopLook } from "@/lib/shop-look";

export function BuyBar({ product }: { product: ShopLook }) {
  const name = displayName(product);

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 overscroll-contain md:hidden" data-testid="shop-ship-bar" translate="no" role="region" aria-label={name}>
      <div
        className="ky-chrome-blur ky-buy-bar liquid-glass-bar border-t border-gold/45 shadow-[0_-18px_44px_-16px_rgba(17,17,17,0.38)]"
        style={{
          paddingBottom: "max(0.75rem, env(safe-area-inset-bottom, 0px))",
          paddingLeft: "max(1rem, env(safe-area-inset-left, 0px))",
          paddingRight: "max(1rem, env(safe-area-inset-right, 0px))",
        }}
      >
        <div className="pt-3">
          <div className="mx-auto flex max-w-6xl items-center gap-3">
            <div className="min-w-0 flex-1">
              <p className="flex min-w-0 items-start gap-x-1.5">
                <MaMark ma={product.ma} className="mt-0.5 shrink-0 text-[10px] tracking-[0.16em] text-muted" />
                <span className="min-w-0 select-none font-display text-[1.15rem] font-medium leading-[1.12] tracking-[0.02em] text-ink line-clamp-2" title={name} translate="no">
                  {name}
                </span>
              </p>
              <ProductPrice
                product={product}
                className="mt-0.5 block text-[13px] font-medium tracking-tight text-ink"
              />
            </div>
            <MessengerCta
              ma={product.ma}
              askPrice={product.priceUsd === null}
              className="min-h-11 shrink-0 whitespace-nowrap"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
