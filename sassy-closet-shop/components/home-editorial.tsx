import { HomeFeatureCards } from "@/components/home-feature-cards";
import { HomeFloatPill } from "@/components/home-float-pill";
import { LookStory } from "@/components/look-story";
import { pickFeatureCards, pickLookStory } from "@/lib/look-story";
import type { MaLetter } from "@/lib/ma";
import type { ShopLook } from "@/lib/shop-look";

/** Scroll stage, category plates, and the floating pill. Hidden while a search is on. */
export function HomeEditorial({
  products,
  types,
}: {
  products: ShopLook[];
  types: MaLetter[];
}) {
  const story = pickLookStory(products);
  const cards = pickFeatureCards(
    products,
    types,
    story.map((look) => look.ma),
  );
  if (story.length < 2 && cards.length === 0) {
    return null;
  }

  return (
    <>
      {story.length >= 2 ? <LookStory looks={story} /> : null}
      {cards.length > 0 ? <HomeFeatureCards cards={cards} /> : null}
      {story.length >= 2 ? <HomeFloatPill looks={story} /> : null}
    </>
  );
}
