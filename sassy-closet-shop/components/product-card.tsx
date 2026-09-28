"use client";

import { useEffect, useMemo, useRef, useState } from "react";
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
  variant = "full",
}: {
  product: ShopLook;
  priority?: boolean;
  namedCover?: boolean;
  variant?: "full" | "compact";
}) {
  const reduced = useReducedMotion();
  const cardRef = useRef<HTMLLIElement>(null);
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

  useEffect(() => {
    const el = cardRef.current;
    if (!el || reduced) {
      return;
    }
    const rect = el.getBoundingClientRect();
    const alreadyVisible = rect.top < window.innerHeight * 0.96 && rect.bottom > 0;
    if (alreadyVisible) {
      return;
    }
    el.dataset.rise = "pending";
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          el.dataset.rise = "shown";
          observer.disconnect();
        }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.18 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [reduced]);

  const compact = variant === "compact";

  return (
    <motion.li
      ref={cardRef}
      variants={fadeUp(Boolean(reduced))}
      exit="exit"
      transition={reduced ? { duration: 0 } : springSoft}
      data-testid="look-card"
      className="sc-rise flex h-full min-w-0 list-none flex-col"
    >
      <Link href={`/m/${product.ma}`} className="group flex min-h-0 flex-1 flex-col touch-manipulation select-none">
        <div className="flex min-h-0 flex-1 flex-col">
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
          <p className="mt-2 px-0.5">
            <MaMark ma={product.ma} className="text-[11px] tracking-[0.16em] text-muted" />
          </p>
          <p className="sc-card-title mt-0.5 px-0.5 min-w-0 font-display text-[1rem] font-medium leading-[1.12] tracking-[0.02em] text-balance text-ink sm:text-[1.125rem]" translate="no">
            {name}
          </p>
          {compact || !description ? null : (
            <p className="sc-card-copy mt-1 px-0.5 text-[13px] leading-[1.35] text-pretty text-muted" translate="no">
              {description}
            </p>
          )}
          <ProductPrice
            product={product}
            className="sc-price mt-auto block px-0.5 pt-2 text-[13px] font-semibold tracking-tight text-ink tabular-nums"
          />
        </div>
      </Link>
      {compact ? null : (
        <>
          <div className="mt-1 px-0.5">
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
        </>
      )}
    </motion.li>
  );
}
