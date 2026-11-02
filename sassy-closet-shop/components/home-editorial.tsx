import { HomeFeatureCards } from "@/components/home-feature-cards";
import { HomeFloatPill } from "@/components/home-float-pill";
import { pickFeatureCards } from "@/lib/home-features";
import type { MaLetter } from "@/lib/ma";
import type { ShopLook } from "@/lib/shop-look";

/** Category plates and the floating pill. Hidden while a search is on. */
export function HomeEditorial({
  products,
  types,
}: {
  products: ShopLook[];
  types: MaLetter[];
}) {
  const cards = pickFeatureCards(products, types);
  if (cards.length === 0) {
    return null;
  }

  return (
    <>
      <HomeFeatureCards cards={cards} />
      <HomeFloatPill />
    </>
  );
}
