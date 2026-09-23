"use client";

import { useLayoutEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence } from "framer-motion";
import { useCatalogMediaVersion } from "@/components/catalog-media-version";
import { ColorNameChips } from "@/components/color-name-chips";
import { GalleryPeekRoll } from "@/components/gallery-peek-roll";
import { PhotoLightbox } from "@/components/photo-lightbox";
import { PlaceholderTile } from "@/components/product-image";
import { SizeNameChips } from "@/components/size-name-chips";
import type { AsiaSizeLetter } from "@/lib/asia-size";
import { cacheBustMediaSrc } from "@/lib/catalog-sha";
import { colorShopLabel } from "@/lib/colors";
import { displayTitle } from "@/lib/copy";
import { clampedReelIndexForColor, productGalleryReel } from "@/lib/gallery-reel";
import { clampGalleryIndex, scrollCurrentChromeIntoView } from "@/lib/gallery-snap";
import {
  COLOR_FIELD_LEGEND,
  SIZE_FIELD_LEGEND,
  ALL_PHOTOS_LABEL,
  emptyGalleryAnnouncement,
  galleryReelLabel,
  messageForRealPhotos,
  morePhotosLabel,
  photoIndexLabel,
  photoPositionLabel,
  viewingColorLine,
} from "@/lib/pdp-copy";
import { imagesForColor, uniqueImageSrcs } from "@/lib/product-media";
import type { ShopLook } from "@/lib/shop-look";
import type { ProductImageAsset } from "@/lib/types";

const THUMB_CAP = 12;

export function ProductGallery({
  product,
  colorId: colorIdProp,
  onColorId,
  showChips = true,
}: {
  product: ShopLook;
  colorId?: string | null;
  onColorId?: (id: string | null) => void;
  showChips?: boolean;
}) {
  const [uncontrolledColorId, setUncontrolledColorId] = useState<string | null>(null);
  const colorId = colorIdProp !== undefined ? colorIdProp : uncontrolledColorId;
  const [sizeLetter, setSizeLetter] = useState<AsiaSizeLetter | null>(null);
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
  const selectedColor = product.colors.find((color) => color.id === colorId);
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

  function chooseColor(id: string) {
    const next = colorId === id ? null : id;
    setColorId(next);
  }

  function chooseSize(letter: AsiaSizeLetter) {
    setSizeLetter((current) => (current === letter ? null : letter));
  }

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
        <div ref={thumbRailRef} className="ky-thumb-rail mt-3 flex min-w-0 max-w-full flex-nowrap gap-2.5 overflow-x-auto tab-scroll">
          {thumbs.map((thumb, thumbIndex) => {
            const src = version ? cacheBustMediaSrc(thumb.src, version) : thumb.src;
            const currentThumb = thumbIndex === safeIndex;
            return (
              <button
                key={`${thumb.src}-${thumbIndex}`}
                type="button"
                aria-label={photoIndexLabel(thumbIndex + 1)}
                aria-current={currentThumb}
                aria-posinset={thumbIndex + 1}
                aria-setsize={reel.length}
                onClick={() => choosePhotoIndex(thumbIndex)}
                className={`ky-thumb-shot relative min-h-11 min-w-11 shrink-0 touch-manipulation select-none overflow-hidden border ${
                  currentThumb ? "border-gold" : "border-gold/35 hover-hover:hover:border-gold"
                }`}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={src} alt="" draggable={false} decoding="async" width={64} height={80} sizes="(min-width: 640px) 72px, 64px" className="h-20 w-16 select-none object-cover object-top sm:h-24 sm:w-[4.5rem]" />
              </button>
            );
          })}
          {overflowCount > 0 ? (
            <button
              type="button"
              data-testid="gallery-more"
              aria-label={morePhotosLabel(overflowCount)}
              aria-current={safeIndex >= THUMB_CAP}
              aria-haspopup="dialog"
              onClick={() => {
                choosePhotoIndex(Math.min(THUMB_CAP, reel.length - 1));
                setLightbox(true);
              }}
              className="flex h-20 min-h-11 w-16 min-w-11 shrink-0 touch-manipulation select-none items-center justify-center whitespace-nowrap border border-gold/35 liquid-glass-chip text-[11px] font-medium uppercase tracking-[0.16em] text-ink hover-hover:hover:border-gold sm:h-24 sm:w-[4.5rem]"
            >
              <span aria-hidden>+{overflowCount}</span>
            </button>
          ) : null}
        </div>
      ) : null}
      {reel.length > 1 ? (
        <p
          className="mt-2 max-w-full truncate whitespace-nowrap text-[11px] uppercase tracking-[0.18em] text-muted tabular-nums"
          aria-hidden
          translate="no"
        >
          {safeIndex + 1} / {slides.length}
        </p>
      ) : null}
      {showChips && product.colors.length > 0 ? (
        <fieldset className="mt-4 border-0 p-0" data-testid="pdp-color-chips">
          <legend className="mb-2 max-w-full truncate whitespace-nowrap text-[11px] uppercase tracking-[0.16em] text-muted" translate="no">
            {COLOR_FIELD_LEGEND}
          </legend>
          <ColorNameChips
            colors={product.colors}
            selectedId={colorId}
            onSelect={chooseColor}
            motionGroupId={`gallery-${product.ma}`}
            hairlineLayoutId="pdp-color"
          />
          {selectedColor ? (
            <p className="sr-only" data-testid="viewing-color" lang="vi">
              {colorHasShots
                ? viewingColorLine(colorShopLabel(selectedColor, Math.max(0, colorIndex)))
                : emptyGalleryAnnouncement(colorLabel)}
            </p>
          ) : null}
          {selectedColor?.note.trim() ? (
            <p className="mt-1 text-pretty text-[13px] text-muted" data-testid="color-note" id={`gallery-${product.ma}-color-note`} translate="no">
              {selectedColor.note.trim()}
            </p>
          ) : null}
        </fieldset>
      ) : null}
      {showChips && product.sizes.length > 0 ? (
        <fieldset className="mt-4 border-0 p-0" data-testid="pdp-size-chips">
          <legend className="mb-2 max-w-full truncate whitespace-nowrap text-[11px] uppercase tracking-[0.16em] text-muted" translate="no">
            {SIZE_FIELD_LEGEND}
          </legend>
          <SizeNameChips
            sizes={product.sizes}
            selectedId={sizeLetter}
            onSelect={chooseSize}
            motionGroupId={`gallery-size-${product.ma}`}
            hairlineLayoutId="pdp-size"
          />
        </fieldset>
      ) : null}
      <AnimatePresence>
        {lightbox && lightboxSlides.length > 0 ? (
          <PhotoLightbox
            key="gallery-lightbox"
            title={displayTitle(product)}
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
