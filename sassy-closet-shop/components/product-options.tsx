"use client";

import { ColorNameChips } from "@/components/color-name-chips";
import { SizeNameChips } from "@/components/size-name-chips";
import type { AsiaSizeLetter } from "@/lib/asia-size";
import { colorShopLabel } from "@/lib/colors";
import {
  COLOR_FIELD_LEGEND,
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

  return (
    <div data-testid="pdp-options">
      {product.colors.length > 0 ? (
        <fieldset className="mt-4 border-0 p-0" data-testid="pdp-color-chips">
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
        <fieldset className="mt-4 border-0 p-0" data-testid="pdp-size-chips">
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
        </fieldset>
      ) : null}
    </div>
  );
}
