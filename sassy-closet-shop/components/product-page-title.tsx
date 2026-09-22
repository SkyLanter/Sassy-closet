import { MaMark } from "@/components/ma-mark";
import { displayName } from "@/lib/copy";
import type { ShopLook } from "@/lib/shop-look";

export function ProductPageTitle({ product }: { product: ShopLook }) {
  return (
    <h1 id="look-title" className="mt-3 flex min-w-0 flex-wrap items-baseline gap-x-2 gap-y-1 text-ink scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)] sm:scroll-mt-[calc(env(safe-area-inset-top,0px)+8.75rem)]">
      <MaMark ma={product.ma} className="select-all text-[11px] tracking-[0.16em] text-muted" />
      <span className="min-w-0 font-display text-[2.15rem] font-medium leading-[1.08] tracking-[0.02em] text-balance sm:text-4xl" translate="no">
        {displayName(product)}
      </span>
    </h1>
  );
}
