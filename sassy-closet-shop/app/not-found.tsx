import type { Metadata } from "next";
import Link from "next/link";
import { ShopEmpty } from "@/components/shop-empty";
import { SITE } from "@/lib/site";

export const metadata: Metadata = {
  title: "Not found",
};

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl ky-gutter py-24" data-testid="shop-not-found">
      <p className="mb-8 text-center font-display text-[1.85rem] font-medium leading-[1.08] tracking-[0.02em] text-balance text-ink" translate="no">
        {SITE.name}
      </p>
      <ShopEmpty
        title="Không tìm thấy · Not found"
        body="Không tìm thấy look trên lookbook · Not found."
      />
      <p className="mt-6 text-center">
        <Link
          href="/"
          aria-label="Về shop · Back to shop"
          translate="no"
          className="liquid-glass-chip inline-flex min-h-11 touch-manipulation select-none items-center whitespace-nowrap rounded-full border border-gold/45 px-4 text-sm text-ink hover-hover:hover:border-gold"
        >
          Back to shop
        </Link>
      </p>
    </div>
  );
}
