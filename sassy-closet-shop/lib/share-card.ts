import { categoryCopy, categoryFromSlug } from "@/lib/categories";
import { displayName } from "@/lib/copy";
import { HOLD_PRICE_LABEL } from "@/lib/dropship-copy";
import { formatUsd } from "@/lib/format";
import type { MaLetter } from "@/lib/ma";
import { loadSharePhoto, type SharePhoto } from "@/lib/share-photo";
import { SITE } from "@/lib/site";
import { FULFILL_LINE_SHORT } from "@/lib/trust-copy";
import type { ShopLook } from "@/lib/shop-look";

export const SHARE_CARD_CTA = "Message us on Messenger";

export type ShareCardFields = {
  kicker: string;
  eyebrow?: string;
  title: string;
  detail?: string;
  cta: string;
};

export type ShareCardModel = ShareCardFields & {
  photo: SharePhoto | null;
};

type PricedLook = {
  ma: string;
  titleEn: string;
  titleVn: string;
  priceUsd: number | null;
};

export function shareCardVariant(model: ShareCardModel): "photo" | "text" {
  return model.photo ? "photo" : "text";
}

export function homeShareCardFields(): ShareCardFields {
  return {
    kicker: "SASSY CLOSET",
    title: SITE.name,
    detail: FULFILL_LINE_SHORT,
    cta: SHARE_CARD_CTA,
  };
}

export function productShareCardCopy(product: PricedLook): ShareCardFields {
  return {
    kicker: "SASSY CLOSET",
    eyebrow: product.ma,
    title: displayName(product),
    detail: product.priceUsd !== null ? formatUsd(product.priceUsd) : HOLD_PRICE_LABEL,
    cta: SHARE_CARD_CTA,
  };
}

export function categoryShareCardFields(type: MaLetter, look?: PricedLook): ShareCardFields {
  return {
    kicker: "SASSY CLOSET",
    eyebrow: look?.ma,
    title: categoryCopy(type).label,
    cta: SHARE_CARD_CTA,
  };
}

export function productSharePlan(
  product: ShopLook | undefined,
): { status: 404 } | { status: 200; fields: ShareCardFields } {
  if (!product) {
    return { status: 404 };
  }
  return { status: 200, fields: productShareCardCopy(product) };
}

export function categorySharePlan(
  slug: string,
  look?: PricedLook,
): { status: 404 } | { status: 200; fields: ShareCardFields } {
  const type = categoryFromSlug(slug);
  if (!type) {
    return { status: 404 };
  }
  return { status: 200, fields: categoryShareCardFields(type, look) };
}

export async function cardWithPhoto(
  fields: ShareCardFields,
  src: string | undefined,
  load: (src: string | undefined) => Promise<SharePhoto | null> = (value) => loadSharePhoto(value),
): Promise<ShareCardModel> {
  let photo: SharePhoto | null = null;
  if (src) {
    try {
      photo = await load(src);
    } catch {
      photo = null;
    }
  }
  return { ...fields, photo };
}
