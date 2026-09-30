import { categoryFilterLabel } from "@/lib/categories";
import { coverSrc } from "@/lib/product-media";
import type { MaLetter } from "@/lib/ma";
import type { ShopLook } from "@/lib/shop-look";

/** Popular looks in the home scroll stage. Caller order is popular order. */
export const LOOK_STORY_LIMIT = 4;

/** Category plates under the stage. One real look each. */
export const FEATURE_CARD_LIMIT = 3;

/** Scroll progress above this leaves the resting carousel and follows the page. */
export const LOOK_STORY_SCROLL_OWN = 0.06;

export const LOOK_STORY_EVENT = "sassy:look-story";

export type LookStoryDetail = {
  ma: string;
  title: string;
  index: number;
};

type TitledLook = {
  ma: string;
  titleEn: string;
  titleVn: string;
};

/** Real catalog title. No invented line, no forced capitals. */
export function editorialTitle(look: TitledLook): string {
  return look.titleEn.trim() || look.titleVn.trim() || look.ma;
}

export function editorialLine(look: ShopLook): string {
  const description = look.descriptionEn.trim() || look.descriptionVn.trim();
  return description || categoryFilterLabel(look.type);
}

export function lookHasCover(look: ShopLook): boolean {
  return Boolean(coverSrc(look));
}

/**
 * First looks in the given order that have a cover.
 * Never adds a mã that was not passed in.
 */
export function pickLookStory(looks: readonly ShopLook[], limit = LOOK_STORY_LIMIT): ShopLook[] {
  const cap = Math.max(0, limit);
  const picked: ShopLook[] = [];
  const seen = new Set<string>();
  for (const look of looks) {
    if (picked.length >= cap) {
      break;
    }
    if (seen.has(look.ma) || !lookHasCover(look)) {
      continue;
    }
    seen.add(look.ma);
    picked.push(look);
  }
  return picked;
}

export type FeatureCardLook = {
  type: MaLetter;
  look: ShopLook;
};

/**
 * One cover per category, in `types` order.
 * Prefers a look that is not already in the scroll stage.
 */
export function pickFeatureCards(
  looks: readonly ShopLook[],
  types: readonly MaLetter[],
  storyMas: readonly string[],
  limit = FEATURE_CARD_LIMIT,
): FeatureCardLook[] {
  const cap = Math.max(0, limit);
  const skip = new Set(storyMas);
  const cards: FeatureCardLook[] = [];
  for (const type of types) {
    if (cards.length >= cap) {
      break;
    }
    const inType = looks.filter((look) => look.type === type && lookHasCover(look));
    const look = inType.find((item) => !skip.has(item.ma)) ?? inType[0];
    if (!look) {
      continue;
    }
    cards.push({ type, look });
  }
  return cards;
}

/** 0 before the stage pins, 1 at the end of the travel. */
export function lookStoryProgress(scrolled: number, travel: number): number {
  if (!Number.isFinite(scrolled) || !Number.isFinite(travel) || travel <= 0) {
    return 0;
  }
  if (scrolled <= 0) {
    return 0;
  }
  if (scrolled >= travel) {
    return 1;
  }
  return scrolled / travel;
}

/** Equal slices. The last look holds through progress 1. */
export function lookStoryIndex(progress: number, count: number): number {
  if (count <= 1) {
    return 0;
  }
  const clamped = Math.min(1, Math.max(0, progress));
  if (clamped >= 1) {
    return count - 1;
  }
  return Math.min(count - 1, Math.floor(clamped * count));
}
