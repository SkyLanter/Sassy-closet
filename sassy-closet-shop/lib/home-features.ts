import { coverSrc } from "@/lib/product-media";
import type { MaLetter } from "@/lib/ma";
import type { ShopLook } from "@/lib/shop-look";

/** Category plates on the home page. One real look each. */
export const FEATURE_CARD_LIMIT = 3;

type TitledLook = {
  ma: string;
  titleEn: string;
  titleVn: string;
};

/** Real catalog title. No invented line, no forced capitals. */
export function editorialTitle(look: TitledLook): string {
  return look.titleEn.trim() || look.titleVn.trim() || look.ma;
}

function lookHasCover(look: ShopLook): boolean {
  return Boolean(coverSrc(look));
}

export type FeatureCardLook = {
  type: MaLetter;
  look: ShopLook;
};

/**
 * One cover per category, in `types` order.
 * Uses the first covered look already in the catalog. Never adds a mã.
 */
export function pickFeatureCards(
  looks: readonly ShopLook[],
  types: readonly MaLetter[],
  limit = FEATURE_CARD_LIMIT,
): FeatureCardLook[] {
  const cap = Math.max(0, limit);
  const cards: FeatureCardLook[] = [];
  for (const type of types) {
    if (cards.length >= cap) {
      break;
    }
    const look = looks.find((item) => item.type === type && lookHasCover(item));
    if (!look) {
      continue;
    }
    cards.push({ type, look });
  }
  return cards;
}
