import { catalogSizeLetters, parseAsiaSizes, type AsiaSizeLetter } from "@/lib/asia-size";
import { ownMaImages } from "@/lib/product-media";
import { customerStockVoiceHit } from "@/lib/public-safety";
import { shopSafeProduct } from "@/lib/sell-contract";
import type { MaLetter } from "@/lib/ma";
import type { Product, ProductColor, ProductImageAsset } from "@/lib/types";

/**
 * Customer-facing look. No ops fields (status / qty / fulfillment / sourceLink).
 * Inbox-price looks are `priceUsd: null` — never stock chrome in the shopper payload.
 * `sizes` are seller/catalog Asia letters already on the row — never invented, never US.
 */
export type ShopLook = {
  ma: string;
  type: MaLetter;
  titleVn: string;
  titleEn: string;
  priceUsd: number | null;
  colors: ProductColor[];
  sizes: AsiaSizeLetter[];
  images: ProductImageAsset[];
  descriptionVn: string;
  descriptionEn: string;
};

export function toShopLook(product: Product): ShopLook {
  const safe = shopSafeProduct(product);
  return {
    ma: safe.ma,
    type: safe.type,
    titleVn: safe.titleVn,
    titleEn: safe.titleEn,
    priceUsd: safe.priceUsd,
    colors: safe.colors,
    sizes: catalogSizeLetters(parseAsiaSizes(safe.sizes)),
    images: ownMaImages(safe),
    descriptionVn: safe.descriptionVn,
    descriptionEn: safe.descriptionEn,
  };
}

export function shopLookAsksPrice(look: ShopLook): boolean {
  return look.priceUsd === null;
}

const OPS_FIELD = /"status"|"sourceLink"|"fulfillment"|"qty"|"fitCm"|"on_hand"/;

export function shopLookPayloadLeak(look: ShopLook): string | null {
  if ("status" in look || "sourceLink" in look || "fulfillment" in look || "qty" in look) {
    return "ops field";
  }
  const json = JSON.stringify(look);
  if (OPS_FIELD.test(json)) {
    return "ops json";
  }
  if (customerStockVoiceHit(json)) {
    return "stock chrome";
  }
  return null;
}
