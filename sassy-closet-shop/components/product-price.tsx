import { cardBuyHint, HOLD_PRICE_LABEL, statusNote } from "@/lib/dropship-copy";
import { formatUsd } from "@/lib/format";
import type { ShopLook } from "@/lib/shop-look";
import type { Product } from "@/lib/types";

function InboxPriceLabel({
  className,
}: {
  className?: string;
}) {
  return <span className={className} translate="no">{HOLD_PRICE_LABEL}</span>;
}

export function ProductPrice({
  product,
  className,
}: {
  product: ShopLook;
  className?: string;
}) {
  if (product.priceUsd === null) {
    return <InboxPriceLabel className={className} />;
  }
  return (
    <span className={[className, "tabular-nums select-all whitespace-nowrap"].filter(Boolean).join(" ")} translate="no">
      {formatUsd(product.priceUsd)}
    </span>
  );
}

export function ProductBuyHint({
  product,
  className,
}: {
  product: Product;
  className?: string;
}) {
  return <p className={className}>{cardBuyHint(product)}</p>;
}

export function ProductStatusNote({ product }: { product: Product }) {
  const sold = product.status === "sold";
  return (
    <p className={`text-sm ${sold ? "text-muted" : "text-gold-deep"}`}>{statusNote(product)}</p>
  );
}
