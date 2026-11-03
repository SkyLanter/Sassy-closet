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

/** 0, or a non-zero integer, with an optional 1–2 digit fraction. No sign or leading zeros. */
const PLAIN_USD_LITERAL = /^(?:0|[1-9]\d*)(?:\.\d{1,2})?$/;
const MAX_SAFE_CENTS_TEXT = String(Number.MAX_SAFE_INTEGER);

/**
 * Dollar text whose cent count is a safe integer.
 * A longer digit string is rejected so Number cannot round it.
 */
function numberFromPlainUsd(literal: string): number {
  if (!PLAIN_USD_LITERAL.test(literal)) {
    return Number.NaN;
  }
  const dot = literal.indexOf(".");
  const whole = dot === -1 ? literal : literal.slice(0, dot);
  const fraction = dot === -1 ? "" : literal.slice(dot + 1);
  const centsDigits = `${whole}${fraction.padEnd(2, "0")}`.replace(/^0+(?=\d)/, "");
  if (
    centsDigits.length > MAX_SAFE_CENTS_TEXT.length ||
    (centsDigits.length === MAX_SAFE_CENTS_TEXT.length && centsDigits > MAX_SAFE_CENTS_TEXT)
  ) {
    return Number.NaN;
  }
  return Number(centsDigits) / 100;
}

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
      return numberFromPlainUsd(trimmed);
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
