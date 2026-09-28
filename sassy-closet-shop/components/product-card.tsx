"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { ColorNameChips } from "@/components/color-name-chips";
import { MaMark } from "@/components/ma-mark";
import { MessengerCta } from "@/components/messenger-cta";
import { ProductImage } from "@/components/product-image";
import { ProductPrice } from "@/components/product-price";
import { colorShopLabel } from "@/lib/colors";
import { displayDescription, displayName } from "@/lib/copy";
import { lookPhotoAlt } from "@/lib/photo-alt";
import { clampedReelIndexForColor, productGalleryReel } from "@/lib/gallery-reel";
import { GALLERY_ROLL_MS } from "@/lib/gallery-snap";
import { fadeUp, springSoft } from "@/lib/motion";
import { shopLookAsksPrice, type ShopLook } from "@/lib/shop-look";

export function ProductCard({
  product,
  priority = false,
  namedCover = true,
}: {
  product: ShopLook;
  priority?: boolean;
  namedCover?: boolean;
}) {
  const reduced = useReducedMotion();
  const name = displayName(product);
  const description = displayDescription(product);
  const [colorId, setColorId] = useState<string | null>(null);
  const reel = useMemo(() => productGalleryReel(product), [product]);
  const slideIndex = clampedReelIndexForColor(reel, colorId);

  function pickColor(id: string) {
    setColorId((current) => (current === id ? null : id));
  }

  const selectedIndex = product.colors.findIndex((color) => color.id === colorId);
  const selectedColor = selectedIndex >= 0 ? product.colors[selectedIndex] : undefined;
  const colorLabel = selectedColor ? colorShopLabel(selectedColor, selectedIndex) : null;

  return (
    <motion.li
      variants={fadeUp(Boolean(reduced))}
      exit="exit"
      transition={springSoft}
      className="sc-rise flex min-w-0 list-none flex-col self-start"
    >
      <Link href={`/m/${product.ma}`} className="group block touch-manipulation select-none">
        <div className="flex flex-col">
          <div
            className="sc-card-well ky-gallery-shell relative aspect-[3/4] w-full shrink-0 overflow-hidden bg-[#f3f1ee] shadow-[0_0_0_0_rgba(17,17,17,0)] motion-safe:transition-[transform,box-shadow] motion-safe:duration-150 motion-safe:ease-[cubic-bezier(0.23,1,0.32,1)] motion-safe:hover-hover:group-hover:-translate-y-1.5 motion-safe:active:scale-[0.98]"
            data-testid="card-cover-reel"
            data-slide-index={String(slideIndex)}
            style={namedCover ? { viewTransitionName: `product-${product.ma}`, contain: "layout" } : undefined}
          >
            {reel.length === 0 ? (
              <ProductImage
                product={product}
                src={undefined}
                alt={lookPhotoAlt({ title: name, ma: product.ma })}
                priority={priority}
                named={false}
                coverFallback={false}
                className="h-full w-full"
              />
            ) : (
              <div
                className="ky-card-reel h-full"
                style={{
                  transform: `translateX(-${slideIndex * 100}%)`,
                  transition: reduced ? "none" : `transform ${GALLERY_ROLL_MS}ms cubic-bezier(0.23, 1, 0.32, 1)`,
                }}
              >
                {reel.map((slide, index) => (
                  <div key={slide.id} className="ky-card-reel-slide">
                    <ProductImage
                      product={product}
                      src={slide.src}
                      alt={lookPhotoAlt({
                        title: name,
                        ma: product.ma,
                        color: slide.colorName,
                        index: slide.photoIndex + 1,
                      })}
                      priority={priority && index === 0}
                      named={false}
                      coverFallback={false}
                      className="h-full w-full"
                    />
                  </div>
                ))}
              </div>
            )}
            <span className="liquid-glass-rim pointer-events-none absolute inset-0 z-[2]" aria-hidden />
            <div className="pointer-events-none absolute inset-0 z-[1] bg-gradient-to-t from-ink/10 via-transparent to-transparent opacity-0 motion-safe:transition-opacity motion-safe:duration-150 motion-safe:hover-hover:group-hover:opacity-70" aria-hidden />
            <span className="pointer-events-none absolute inset-x-0 bottom-0 z-[2] h-px origin-center scale-x-100 bg-gold/45" aria-hidden />
          </div>
          <p className="mt-2.5 px-0.5">
            <MaMark ma={product.ma} className="text-[10px] tracking-[0.16em] text-muted" />
          </p>
          <p className="sc-card-title mt-0.5 px-0.5 font-display text-[1.15rem] font-medium leading-[1.15] tracking-[0.02em] text-ink sm:text-[1.25rem]" translate="no">
            {name}
          </p>
          <p className="sc-card-copy mt-1.5 px-0.5 text-[12.5px] leading-[1.35] text-muted" translate="no">
            {description}
          </p>
          <ProductPrice
            product={product}
            className="mt-auto block px-0.5 pt-2 text-[13px] font-semibold tracking-tight text-ink tabular-nums"
          />
        </div>
      </Link>
      <div className="mt-1.5 px-0.5">
        <MessengerCta
          ma={product.ma}
          askPrice={shopLookAsksPrice(product)}
          variant="card"
          colorLabel={colorLabel}
        />
      </div>
      {product.colors.length > 0 ? (
        <div className="mt-2 min-w-0 px-0.5">
          <ColorNameChips
            colors={product.colors}
            selectedId={colorId}
            onSelect={pickColor}
            size="sm"
            motionGroupId={`card-${product.ma}`}
          />
        </div>
      ) : (
        <div className="mt-2 min-h-11" aria-hidden />
      )}
    </motion.li>
  );
}
