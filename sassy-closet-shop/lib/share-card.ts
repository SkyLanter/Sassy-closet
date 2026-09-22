import { HOLD_PRICE_LABEL } from "@/lib/dropship-copy";
import { formatUsd } from "@/lib/format";
import { normalizeMa } from "@/lib/ma";
import { categoryCopy, categoryFromSlug } from "@/lib/categories";
import { FULFILL_LINE_SHORT, productShareTitle } from "@/lib/trust-copy";
import type { ShopLook } from "@/lib/shop-look";

export type ShareCardCopy = {
  kicker: string;
  title: string;
  subtitle: string;
  footer: string;
};

export function productShareCardCopy(product: ShopLook | undefined, rawMa: string): ShareCardCopy {
  if (!product) {
    return {
      kicker: "Sassy Closet",
      title: normalizeMa(rawMa) || "Lookbook",
      subtitle: "Message on Messenger",
      footer: "Message on Messenger",
    };
  }

  return {
    kicker: "Sassy Closet",
    title: productShareTitle(product),
    subtitle: product.priceUsd !== null ? formatUsd(product.priceUsd) : HOLD_PRICE_LABEL,
    footer: "Message on Messenger",
  };
}

export function categoryShareCardCopy(slug: string): ShareCardCopy {
  const type = categoryFromSlug(slug);
  return {
    kicker: "Sassy Closet",
    title: type ? categoryCopy(type).label : "Collection",
    subtitle: FULFILL_LINE_SHORT,
    footer: "Message on Messenger",
  };
}
