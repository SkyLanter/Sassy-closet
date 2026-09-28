import { MaMark } from "@/components/ma-mark";
import { displayName } from "@/lib/copy";
import type { ShopLook } from "@/lib/shop-look";

export function ProductPageTitle({ product }: { product: ShopLook }) {
  return (
    <h1
      id="look-title"
      className="mt-3 min-w-0 scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)] text-ink sm:scroll-mt-[calc(env(safe-area-inset-top,0px)+8.75rem)]"
    >
      <span className="flex min-h-11 items-center gap-1.5 text-[11px] uppercase tracking-[0.16em] text-muted">
        <span translate="no">Mã:</span>
        <MaMark ma={product.ma} className="select-all text-ink" />
      </span>
      <span className="sc-title mt-1 block font-display text-[2.15rem] font-medium leading-[1.05] tracking-[0.02em] sm:text-4xl" translate="no">
        {displayName(product)}
      </span>
    </h1>
  );
}
