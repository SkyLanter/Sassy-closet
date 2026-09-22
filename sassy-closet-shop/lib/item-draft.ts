import {
  assertAsiaSizesOnly,
  assertStoredFitCm,
  type AsiaSizeLetter,
  type ShopSize,
  type FitCm,
} from "@/lib/asia-size";
import type { Fulfillment } from "@/lib/fulfillment";
import { isAllowedImageSrc } from "@/lib/product-parse";
import { parseSourceLink } from "@/lib/source-link";
import type { ProductColor, ProductImageAsset, ProductStatus } from "@/lib/types";
import { warehouseVoiceError } from "@/lib/warehouse-voice";

export type ItemDraft = {
  titleEn: string;
  titleVn: string;
  descriptionEn: string;
  descriptionVn: string;
  status: ProductStatus;
  priceInput: string;
  colors: ProductColor[];
  images: ProductImageAsset[];
  sizes: ShopSize[];
  fitCm: FitCm;
  fulfillment: Fulfillment;
  sourceLink: string;
};

export function parseDraftPrice(status: ProductStatus, priceInput: string): number | null | typeof Number.NaN {
  switch (status) {
    case "hold":
      return null;
    case "available":
    case "sold": {
      const trimmed = priceInput.trim();
      if (!trimmed) {
        return null;
      }
      const value = Number(trimmed);
      return Number.isFinite(value) ? value : Number.NaN;
    }
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

export function validateItemDraft(draft: ItemDraft): string | null {
  if (!draft.titleEn.trim()) {
    return "English title is required.";
  }
  if (draft.images.some((image) => image.src.startsWith("blob:"))) {
    return "Wait for the image upload to finish before saving.";
  }
  const priceUsd = parseDraftPrice(draft.status, draft.priceInput);
  if (draft.status === "available" && (priceUsd === null || Number.isNaN(priceUsd))) {
    return "Available items need a USD price.";
  }
  if (draft.status === "sold" && priceUsd !== null && Number.isNaN(priceUsd)) {
    return "Sold items need a valid USD price or a blank price.";
  }
  for (const color of draft.colors) {
    if (!color.name.trim()) {
      return "Each color needs a name. The shop shows names, not color boxes.";
    }
  }
  try {
    assertAsiaSizesOnly(draft.sizes);
    assertStoredFitCm(draft.fitCm);
  } catch (error) {
    return error instanceof Error ? error.message : "Size / fit is invalid.";
  }
  for (const image of draft.images) {
    const src = image.src.trim();
    if (!src) {
      continue;
    }
    if (!isAllowedImageSrc(src)) {
      return `Invalid image URL: ${src}`;
    }
  }
  if (draft.sourceLink.trim()) {
    try {
      parseSourceLink(draft.sourceLink);
    } catch (error) {
      return error instanceof Error
        ? error.message
        : "Source link must be a real Taobao URL (e.tb.cn). Do not invent one.";
    }
  }
  return warehouseVoiceError(draft.descriptionEn, draft.descriptionVn, draft.fulfillment);
}
