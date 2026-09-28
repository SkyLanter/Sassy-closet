"use client";

import { useState } from "react";
import Link from "next/link";
import { BuyBar } from "@/components/buy-bar";
import { ContentWaveLooks } from "@/components/content-wave";
import { CopyMa } from "@/components/copy-ma";
import { FitNotes } from "@/components/fit-notes";
import { MessengerCta } from "@/components/messenger-cta";
import { ProductDescription } from "@/components/product-description";
import { ProductGallery } from "@/components/product-gallery";
import { ProductMaLine, ProductPageTitle } from "@/components/product-page-title";
import { ProductPrice } from "@/components/product-price";
import { categoryAriaLabel, categoryCopy, categoryHref } from "@/lib/categories";
import type { ShopLook } from "@/lib/shop-look";

export function ProductLook({ product }: { product: ShopLook }) {
  const type = categoryCopy(product.type);
  const [ask, setAsk] = useState<{ size: string | null; color: string | null }>({
    size: null,
    color: null,
  });

  return (
    <>
    <article aria-labelledby="look-title" className="mx-auto grid max-w-7xl gap-8 ky-gutter py-8 lg:grid-cols-2 lg:gap-14 lg:py-12">
      <ContentWaveLooks>
        <ProductGallery product={product} onAskChange={setAsk} />
      </ContentWaveLooks>
      <div className="flex min-w-0 flex-col lg:pt-4">
        <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-[11px] uppercase tracking-[0.18em] text-muted">
          <Link
            href={categoryHref(product.type)}
            aria-label={categoryAriaLabel(product.type)}
            translate="no"
            className="inline-flex min-h-11 touch-manipulation select-none items-center hover-hover:hover:text-ink"
          >
            {type.label}
          </Link>
          <span aria-hidden>/</span>
          <CopyMa ma={product.ma} />
        </p>
        <ProductPageTitle product={product} />
        <ProductPrice
          product={product}
          className="sc-price mt-3 block text-[1.35rem] font-semibold tracking-tight text-ink sm:text-[1.5rem]"
        />
        <ProductMaLine ma={product.ma} />
        <ProductDescription product={product} />
        <FitNotes measurements={product.measurements} />
        <div className="mt-8 hidden md:block">
          <MessengerCta
            ma={product.ma}
            sizeLabel={ask.size}
            colorLabel={ask.color}
            askPrice={product.priceUsd === null}
          />
        </div>
      </div>
    </article>
    <BuyBar product={product} sizeLabel={ask.size} colorLabel={ask.color} />
    </>
  );
}
