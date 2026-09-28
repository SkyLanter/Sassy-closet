import { MaMark } from "@/components/ma-mark";
import { displayName } from "@/lib/copy";
import type { ShopLook } from "@/lib/shop-look";

export function ProductPageTitle({ product }: { product: ShopLook }) {
  return (
    <h1
      id="look-title"
      className="mt-1 min-w-0 scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)] text-ink outline-none sm:scroll-mt-[calc(env(safe-area-inset-top,0px)+8.75rem)]"
    >
      <span className="mb-1 flex min-h-0 items-center uppercase text-[11px] tracking-[0.16em] text-muted">
        <MaMark ma={product.ma} className="select-all text-[11px] tracking-[0.16em]" />
      </span>
      <span className="sc-title block font-display text-[2.05rem] font-medium leading-[1.08] tracking-[0.02em] text-balance sm:text-4xl" translate="no">
        {displayName(product)}
      </span>
    </h1>
  );
}
