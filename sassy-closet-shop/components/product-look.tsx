"use client";

import { useState } from "react";
import Link from "next/link";
import { BuyBar } from "@/components/buy-bar";
import { ContentWaveLooks } from "@/components/content-wave";
import { CopyMa } from "@/components/copy-ma";
import { ShareLook } from "@/components/share-look";
import { FitNotes } from "@/components/fit-notes";
import { MessengerCta } from "@/components/messenger-cta";
import { ProductDescription } from "@/components/product-description";
import { ProductGallery } from "@/components/product-gallery";
import { ProductOptions } from "@/components/product-options";
import { ProductPageTitle } from "@/components/product-page-title";
import { ProductPrice } from "@/components/product-price";
import type { AsiaSizeLetter } from "@/lib/asia-size";
import { categoryAriaLabel, categoryCopy, categoryHref } from "@/lib/categories";
import { colorShopLabel } from "@/lib/colors";
import { imagesForColor, uniqueImageSrcs } from "@/lib/product-media";
import { ORDER_VIA_MESSENGER } from "@/lib/pdp-copy";
import { productShareTitle } from "@/lib/trust-copy";
import type { ShopLook } from "@/lib/shop-look";

export function ProductLook({ product }: { product: ShopLook }) {
  const type = categoryCopy(product.type);
  const [colorId, setColorId] = useState<string | null>(null);
  const [sizeLetter, setSizeLetter] = useState<AsiaSizeLetter | null>(null);
  const colorIndex = product.colors.findIndex((color) => color.id === colorId);
  const selectedColor = colorIndex >= 0 ? product.colors[colorIndex] : undefined;
  const colorLabel = selectedColor ? colorShopLabel(selectedColor, colorIndex) : null;
  const colorHasShots = colorId === null || uniqueImageSrcs(imagesForColor(product, colorId)).length > 0;

  function chooseColor(id: string) {
    setColorId((current) => (current === id ? null : id));
  }

  function chooseSize(letter: AsiaSizeLetter) {
    setSizeLetter((current) => (current === letter ? null : letter));
  }

  return (
    <>
    <article aria-labelledby="look-title" className="ky-pdp mx-auto grid max-w-7xl items-start gap-1 ky-gutter py-1 lg:grid-cols-2 lg:gap-x-14 lg:gap-y-5 lg:py-8">
      <div className="ky-pdp-heading flex min-w-0 items-baseline justify-between gap-x-3 lg:col-span-2">
        <ProductPageTitle product={product} />
        <ProductPrice
          product={product}
          className="ky-pdp-price sc-price shrink-0 text-[1.15rem] font-semibold tracking-tight text-ink sm:text-[1.5rem]"
        />
      </div>
      <div className="ky-pdp-media min-w-0 lg:sticky lg:top-[calc(env(safe-area-inset-top,0px)+8.75rem)] lg:self-start">
        <ContentWaveLooks>
          <ProductGallery product={product} colorId={colorId} onColorId={setColorId} />
        </ContentWaveLooks>
      </div>
      <div className="ky-pdp-copy flex min-w-0 flex-col">
        <p className="ky-pdp-meta flex min-w-0 flex-nowrap items-center gap-x-2 overflow-x-auto tab-scroll text-[11px] uppercase tracking-[0.18em] text-muted">
          <Link
            href={categoryHref(product.type)}
            aria-label={categoryAriaLabel(product.type)}
            translate="no"
            className="inline-flex min-h-11 shrink-0 touch-manipulation select-none items-center whitespace-nowrap hover-hover:hover:text-ink"
          >
            {type.label}
          </Link>
          <span className="shrink-0" aria-hidden>/</span>
          <CopyMa ma={product.ma} />
          <ShareLook ma={product.ma} title={productShareTitle(product)} />
        </p>
        <ProductOptions
          product={product}
          colorId={colorId}
          onColor={chooseColor}
          sizeLetter={sizeLetter}
          onSize={chooseSize}
          colorHasShots={colorHasShots}
        />
        <div className="ky-pdp-rest">
        <ProductDescription product={product} />
        <FitNotes measurements={product.measurements} />
        <div className="mt-6 hidden md:block">
          <MessengerCta
            ma={product.ma}
            sizeLabel={sizeLetter}
            colorLabel={colorLabel}
            askPrice={product.priceUsd === null}
          />
          <p className="mt-2 text-[11px] uppercase tracking-[0.14em] text-muted" translate="no">
            {ORDER_VIA_MESSENGER}
          </p>
        </div>
        </div>
      </div>
    </article>
    <BuyBar product={product} sizeLabel={sizeLetter} colorLabel={colorLabel} />
    </>
  );
}
