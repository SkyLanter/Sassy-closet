"use client";

import { MaMark } from "@/components/ma-mark";
import { MessengerCta } from "@/components/messenger-cta";
import { ProductPrice } from "@/components/product-price";
import { displayName } from "@/lib/copy";
import { ORDER_VIA_MESSENGER } from "@/lib/pdp-copy";
import type { ShopLook } from "@/lib/shop-look";

export function BuyBar({
  product,
  sizeLabel = null,
  colorLabel = null,
}: {
  product: ShopLook;
  sizeLabel?: string | null;
  colorLabel?: string | null;
}) {
  const name = displayName(product);

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 overscroll-contain md:hidden" data-testid="shop-ship-bar" translate="no" role="region" aria-label={name}>
      <div
        className="ky-chrome-blur ky-buy-bar liquid-glass-bar border-t border-gold/45"
        style={{
          paddingBottom: "max(0.375rem, env(safe-area-inset-bottom, 0px))",
          paddingLeft: "max(1rem, env(safe-area-inset-left, 0px))",
          paddingRight: "max(1rem, env(safe-area-inset-right, 0px))",
        }}
      >
        <div className="pt-1">
          <div className="mx-auto max-w-6xl">
            <div className="flex items-center gap-3">
              <div className="min-w-0 flex-1">
                <p className="flex min-w-0 items-center gap-x-1.5">
                  <MaMark ma={product.ma} className="shrink-0 text-[11px] tracking-[0.16em] text-muted" />
                  <span className="min-w-0 flex-1 select-none overflow-hidden text-ellipsis whitespace-nowrap font-display text-[15px] font-medium leading-[1.15] tracking-[0.01em] text-ink" title={name} translate="no">
                    {name}
                  </span>
                </p>
                <ProductPrice
                  product={product}
                  className="mt-0.5 block truncate text-[13px] font-medium tracking-tight text-ink"
                />
              </div>
              <MessengerCta
                ma={product.ma}
                sizeLabel={sizeLabel}
                colorLabel={colorLabel}
                askPrice={product.priceUsd === null}
                className="min-h-11 shrink-0 whitespace-nowrap"
              />
            </div>
            <p className="mt-0.5 whitespace-nowrap text-[10px] font-medium uppercase leading-none tracking-[0.08em] text-muted" translate="no">
              {ORDER_VIA_MESSENGER}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
