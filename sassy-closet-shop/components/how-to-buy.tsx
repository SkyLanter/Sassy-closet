import Link from "next/link";
import { MaMark } from "@/components/ma-mark";
import type { Product } from "@/lib/types";

export function HowToBuy({
  product,
}: {
  product?: Product;
}) {
  return (
    <p className="mt-3 text-sm text-muted" data-testid="shop-how-to-buy">
      Message {product ? <MaMark ma={product.ma} className="text-[13px] tracking-[0.12em] text-ink" /> : "us"} on{" "}
      <Link href="/" className="text-gold-deep hover-hover:hover:text-ink">
        Messenger
      </Link>
      .
    </p>
  );
}
