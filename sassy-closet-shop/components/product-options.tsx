"use client";

import { ColorNameChips } from "@/components/color-name-chips";
import { SizeNameChips } from "@/components/size-name-chips";
import { useSiteSettings } from "@/components/site-settings";
import type { AsiaSizeLetter } from "@/lib/asia-size";
import { colorShopLabel } from "@/lib/colors";
import { messengerSizeAskHref } from "@/lib/messenger-ask";
import {
  COLOR_FIELD_LEGEND,
  SIZE_ASK_LABEL,
  SIZE_FIELD_LEGEND,
  emptyGalleryAnnouncement,
  viewingColorLine,
} from "@/lib/pdp-copy";
import type { ShopLook } from "@/lib/shop-look";

export function ProductOptions({
  product,
  colorId,
  onColor,
  sizeLetter,
  onSize,
  colorHasShots,
}: {
  product: ShopLook;
  colorId: string | null;
  onColor: (id: string) => void;
  sizeLetter: AsiaSizeLetter | null;
  onSize: (letter: AsiaSizeLetter) => void;
  colorHasShots: boolean;
}) {
  const selectedColor = product.colors.find((color) => color.id === colorId);
  const colorIndex = product.colors.findIndex((color) => color.id === colorId);
  const colorLabel =
    colorIndex >= 0 && product.colors[colorIndex]
      ? colorShopLabel(product.colors[colorIndex], colorIndex)
      : "";
  const { facebookPageUrl } = useSiteSettings();
  const sizeAskHref = messengerSizeAskHref(
    facebookPageUrl,
    product.ma,
    sizeLetter,
    colorLabel || null,
  );

  return (
    <div className="ky-pdp-options" data-testid="pdp-options">
      {product.colors.length > 0 ? (
        <fieldset className="ky-pdp-colors mt-4 border-0 p-0" data-testid="pdp-color-chips">
          <legend className="mb-2 max-w-full truncate whitespace-nowrap text-[11px] uppercase tracking-[0.16em] text-muted" translate="no">
            {COLOR_FIELD_LEGEND}
          </legend>
          <ColorNameChips
            colors={product.colors}
            selectedId={colorId}
            onSelect={onColor}
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
      {product.sizes.length > 0 ? (
        <fieldset className="ky-pdp-sizes mt-4 border-0 p-0" data-testid="pdp-size-chips">
          <legend className="mb-2 max-w-full truncate whitespace-nowrap text-[11px] uppercase tracking-[0.16em] text-muted" translate="no">
            {SIZE_FIELD_LEGEND}
          </legend>
          <SizeNameChips
            sizes={product.sizes}
            selectedId={sizeLetter}
            onSelect={onSize}
            motionGroupId={`gallery-size-${product.ma}`}
            hairlineLayoutId="pdp-size"
          />
          {sizeAskHref ? (
            <a
              href={sizeAskHref}
              target="_blank"
              rel="noopener noreferrer"
              referrerPolicy="no-referrer"
              data-testid="size-ask"
              className="mt-1 inline-flex min-h-11 items-center text-[12px] leading-snug text-muted underline decoration-gold/50 underline-offset-4 hover-hover:hover:text-ink"
              translate="no"
            >
              {SIZE_ASK_LABEL}
            </a>
          ) : null}
        </fieldset>
      ) : null}
    </div>
  );
}
