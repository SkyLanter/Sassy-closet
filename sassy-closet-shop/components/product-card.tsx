"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { ColorNameChips } from "@/components/color-name-chips";
import { MaMark } from "@/components/ma-mark";
import { MessengerCta } from "@/components/messenger-cta";
import { ProductImage } from "@/components/product-image";
import { ProductPrice } from "@/components/product-price";
import { displayDescription, displayName } from "@/lib/copy";
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
  const [waterRoll, setWaterRoll] = useState(false);
  const skipWater = useRef(true);

  useEffect(() => {
    if (skipWater.current) {
      skipWater.current = false;
      return;
    }
    if (reduced || reel.length < 2) {
      return;
    }
    setWaterRoll(true);
    const timer = window.setTimeout(() => setWaterRoll(false), GALLERY_ROLL_MS + 40);
    return () => window.clearTimeout(timer);
  }, [reduced, reel.length, slideIndex]);

  function pickColor(id: string) {
    setColorId((current) => (current === id ? null : id));
  }

  return (
    <motion.li
      variants={fadeUp(Boolean(reduced))}
      exit="exit"
      transition={springSoft}
      className="min-w-0 list-none"
    >
      <Link href={`/m/${product.ma}`} className="group block touch-manipulation">
        <div
          className="ky-gallery-shell relative aspect-[3/4] overflow-hidden bg-[#f3f1ee] shadow-[0_0_0_0_rgba(17,17,17,0)] motion-safe:transition-[transform,box-shadow] motion-safe:duration-500 motion-safe:ease-out motion-safe:hover-hover:group-hover:-translate-y-1.5 motion-safe:hover-hover:group-hover:shadow-[0_12px_28px_-22px_rgba(17,17,17,0.32)]"
          data-testid="card-cover-reel"
          data-slide-index={String(slideIndex)}
          data-water-roll={waterRoll ? "1" : "0"}
          style={namedCover ? { viewTransitionName: `product-${product.ma}`, contain: "layout" } : undefined}
        >
          {reel.length === 0 ? (
            <ProductImage
              product={product}
              src={undefined}
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
                transition: reduced ? "none" : `transform ${GALLERY_ROLL_MS}ms cubic-bezier(0.22, 1, 0.36, 1)`,
              }}
            >
              {reel.map((slide, index) => (
                <div key={slide.id} className="ky-card-reel-slide">
                  <ProductImage
                    product={product}
                    src={slide.src}
                    priority={priority && index === 0}
                    named={false}
                    coverFallback={false}
                    className="h-full w-full"
                  />
                </div>
              ))}
            </div>
          )}
          {reel.length > 1 ? <div className="gallery-water-sheen" aria-hidden /> : null}
          <div className="pointer-events-none absolute inset-0 z-[1] bg-gradient-to-t from-ink/16 via-transparent to-transparent opacity-0 motion-safe:transition-opacity motion-safe:duration-500 motion-safe:hover-hover:group-hover:opacity-100" aria-hidden />
          <span className="pointer-events-none absolute inset-x-0 bottom-0 z-[2] h-px origin-center scale-x-100 bg-gold/45" aria-hidden />
        </div>
        <p className="mt-2 flex flex-wrap items-baseline gap-x-1.5 px-0.5 text-ink">
          <MaMark ma={product.ma} className="text-[10px] tracking-[0.16em] text-muted" />
          <span className="min-w-0 font-display text-[1.15rem] font-medium leading-[1.12] tracking-[0.02em] text-balance sm:text-[1.25rem]" translate="no">
            {name}
          </span>
        </p>
        <ProductPrice
          product={product}
          className="mt-1 block px-0.5 text-[13px] font-medium tracking-tight text-ink"
        />
        {description ? (
          <p className="mt-1 line-clamp-2 px-0.5 text-[11px] leading-[1.35] text-pretty text-muted" translate="no">
            {description}
          </p>
        ) : null}
      </Link>
      <div className="mt-1.5 px-0.5">
        <MessengerCta
          ma={product.ma}
          askPrice={shopLookAsksPrice(product)}
          variant="card"
        />
      </div>
      {product.colors.length > 0 ? (
        <div className="mt-2 px-0.5">
          <ColorNameChips
            colors={product.colors}
            selectedId={colorId}
            onSelect={pickColor}
            size="sm"
            motionGroupId={`card-${product.ma}`}
          />
        </div>
      ) : null}
    </motion.li>
  );
}
