"use client";

import { useLayoutEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence } from "framer-motion";
import { useCatalogMediaVersion } from "@/components/catalog-media-version";
import { GalleryPeekRoll } from "@/components/gallery-peek-roll";
import { PhotoLightbox } from "@/components/photo-lightbox";
import { FallibleLookPhoto, PlaceholderTile } from "@/components/product-image";
import { cacheBustMediaSrc } from "@/lib/catalog-sha";
import { colorShopLabel } from "@/lib/colors";
import { displayTitle } from "@/lib/copy";
import { clampedReelIndexForColor, productGalleryReel } from "@/lib/gallery-reel";
import { clampGalleryIndex, scrollCurrentChromeIntoView } from "@/lib/gallery-snap";
import {
  ALL_PHOTOS_LABEL,
  emptyGalleryAnnouncement,
  galleryReelLabel,
  messageForRealPhotos,
  morePhotosLabel,
  photoIndexLabel,
  photoPositionLabel,
} from "@/lib/pdp-copy";
import { imagesForColor, uniqueImageSrcs } from "@/lib/product-media";
import type { ShopLook } from "@/lib/shop-look";
import type { ProductImageAsset } from "@/lib/types";

const THUMB_CAP = 12;

export function ProductGallery({
  product,
  colorId: colorIdProp,
  onColorId,
}: {
  product: ShopLook;
  colorId?: string | null;
  onColorId?: (id: string | null) => void;
}) {
  const [uncontrolledColorId, setUncontrolledColorId] = useState<string | null>(null);
  const colorId = colorIdProp !== undefined ? colorIdProp : uncontrolledColorId;
  const [index, setIndex] = useState(0);
  const [lightbox, setLightbox] = useState(false);
  const thumbRailRef = useRef<HTMLDivElement>(null);
  const version = useCatalogMediaVersion();
  const reel = useMemo(() => productGalleryReel(product), [product]);

  function setColorId(next: string | null) {
    onColorId?.(next);
    if (colorIdProp === undefined) {
      setUncontrolledColorId(next);
    }
  }
  const selectedShots = useMemo(
    () => uniqueImageSrcs(imagesForColor(product, colorId)),
    [colorId, product],
  );
  const slides = useMemo(
    () =>
      reel.map((slide) => ({
        ...slide,
        src: version ? cacheBustMediaSrc(slide.src, version) : slide.src,
      })),
    [reel, version],
  );
  const lightboxSlides: ProductImageAsset[] = useMemo(
    () =>
      reel.map((slide, order) => ({
        src: slide.src,
        colorId: slide.colorId,
        order: order + 1,
      })),
    [reel],
  );
  const colorIndex = product.colors.findIndex((color) => color.id === colorId);
  const colorLabel =
    colorIndex >= 0 && product.colors[colorIndex]
      ? colorShopLabel(product.colors[colorIndex], colorIndex)
      : ALL_PHOTOS_LABEL;
  const safeIndex = clampGalleryIndex(index, slides.length);
  const overflowCount = Math.max(0, reel.length - THUMB_CAP);
  const thumbs = reel.slice(0, THUMB_CAP);
  const colorHasShots = colorId === null || selectedShots.length > 0;

  useLayoutEffect(() => {
    const target = clampedReelIndexForColor(reel, colorId);
    setIndex((current) => (current === target ? current : target));
  }, [colorId, reel]);

  useLayoutEffect(() => {
    scrollCurrentChromeIntoView(thumbRailRef.current);
  }, [safeIndex, thumbs.length, overflowCount]);

  function choosePhotoIndex(nextPhoto: number) {
    const clamped = clampGalleryIndex(nextPhoto, slides.length);
    setIndex(clamped);
    const slide = reel[clamped];
    if (slide?.colorId) {
      setColorId(slide.colorId);
    }
  }

  return (
    <div data-testid="product-gallery">
      {slides.length === 0 ? (
        <div
          className="ky-gallery-frame relative aspect-[3/4] overflow-hidden border border-gold/45 bg-[#f4f1ec]"
          data-testid="gallery-empty"
          role="img"
          aria-label={galleryReelLabel(product.ma)}
          style={{ viewTransitionName: `product-${product.ma}` }}
        >
          <PlaceholderTile ma={product.ma} letter={product.type} decorative />
          <p className="liquid-glass-caption pointer-events-none absolute inset-x-0 bottom-5 mx-auto w-max max-w-[90%] truncate whitespace-nowrap rounded-md px-3 py-1.5 text-center text-[11px] font-medium uppercase tracking-[0.16em] select-none" aria-hidden translate="no">
            {messageForRealPhotos(product.ma)}
          </p>
        </div>
      ) : (
        <div
          className="ky-gallery-frame relative aspect-[3/4] overflow-hidden bg-[#f3f1ee]"
          data-testid="gallery-frame"
          style={{ viewTransitionName: `product-${product.ma}`, contain: "layout" }}
        >
          <GalleryPeekRoll
            slides={slides}
            index={safeIndex}
            ma={product.ma}
            letter={product.type}
            onIndexChange={choosePhotoIndex}
            onCenterClick={colorHasShots ? () => setLightbox(true) : undefined}
          />
          {!colorHasShots ? (
            <div
              className="pointer-events-auto absolute inset-0 z-[25] flex items-end justify-center bg-ink/35 pdp-lightbox-veil"
              data-testid="gallery-color-empty"
            >
              <p className="liquid-glass-caption mb-5 mx-3 max-w-[90%] rounded-md px-3 py-2 text-center text-[11px] leading-relaxed text-pretty select-none" aria-hidden translate="no">
                {emptyGalleryAnnouncement(colorLabel)}
              </p>
            </div>
          ) : null}
          {reel.length > 1 && colorHasShots ? (
            <p
              className="gallery-photo-count pointer-events-none absolute top-3 right-3 z-[4] max-w-[70%] truncate rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] text-muted tabular-nums"
              data-testid="gallery-photo-count"
              aria-hidden
              translate="no"
            >
              {safeIndex + 1} / {slides.length}
            </p>
          ) : null}
        </div>
      )}
      {slides.length > 0 ? (
        <p className="sr-only" aria-live="polite" translate="no">
          {!colorHasShots
            ? emptyGalleryAnnouncement(colorLabel)
            : `${colorLabel}. ${photoPositionLabel(safeIndex + 1, slides.length)}.`}
        </p>
      ) : null}
      {reel.length > 0 ? (
        <div ref={thumbRailRef} className="ky-thumb-rail sc-thumb-rail mt-0 flex min-w-0 max-w-full flex-nowrap gap-2 overflow-x-auto tab-scroll">
          {thumbs.map((thumb, thumbIndex) => {
            const src = version ? cacheBustMediaSrc(thumb.src, version) : thumb.src;
            const currentThumb = thumbIndex === safeIndex;
            return (
              <button
                key={`${thumb.src}-${thumbIndex}`}
                type="button"
                aria-label={photoIndexLabel(thumbIndex + 1)}
                aria-current={currentThumb ? "true" : undefined}
                onClick={() => choosePhotoIndex(thumbIndex)}
                className={`ky-thumb-shot relative aspect-[3/4] min-h-11 min-w-11 max-w-[4.25rem] flex-1 touch-manipulation select-none overflow-hidden border ${
                  currentThumb ? "sc-thumb-active border-gold-deep" : "border-gold/35 hover-hover:hover:border-gold"
                }`}
              >
                <FallibleLookPhoto
                  src={src}
                  alt=""
                  sizes="(min-width: 640px) 72px, 64px"
                  width={64}
                  height={85}
                  className="object-cover object-top"
                  ma={product.ma}
                  letter={product.type}
                  compact
                />
              </button>
            );
          })}
          {overflowCount > 0 ? (
            <button
              type="button"
              data-testid="gallery-more"
              aria-label={morePhotosLabel(overflowCount)}
              aria-current={safeIndex >= THUMB_CAP ? "true" : undefined}
              aria-haspopup="dialog"
              onClick={() => {
                choosePhotoIndex(Math.min(THUMB_CAP, reel.length - 1));
                setLightbox(true);
              }}
              className="ky-thumb-shot relative flex aspect-[3/4] min-h-11 min-w-11 max-w-[4.25rem] flex-1 touch-manipulation select-none items-center justify-center whitespace-nowrap border border-gold/35 liquid-glass-chip text-[11px] font-medium uppercase tracking-[0.16em] text-ink hover-hover:hover:border-gold"
            >
              <span aria-hidden>+{overflowCount}</span>
            </button>
          ) : null}
        </div>
      ) : null}
      <AnimatePresence>
        {lightbox && lightboxSlides.length > 0 ? (
          <PhotoLightbox
            key="gallery-lightbox"
            title={displayTitle(product)}
            ma={product.ma}
            letter={product.type}
            colorLabel={colorLabel}
            slides={lightboxSlides}
            index={safeIndex}
            version={version}
            onClose={() => setLightbox(false)}
            onIndex={choosePhotoIndex}
          />
        ) : null}
      </AnimatePresence>
    </div>
  );
}
