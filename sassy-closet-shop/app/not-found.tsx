import type { Metadata } from "next";
import Link from "next/link";
import { ShopEmpty } from "@/components/shop-empty";

export const metadata: Metadata = {
  title: "Not found",
};

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl ky-gutter py-24">
      <h1 className="sr-only" translate="no">
        Không tìm thấy · Not found
      </h1>
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
