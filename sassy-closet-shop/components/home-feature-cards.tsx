"use client";

import Link from "next/link";
import { ProductImage } from "@/components/product-image";
import { useQuietRise } from "@/components/use-quiet-rise";
import { categoryAriaLabel, categoryFilterLabel, categorySectionId } from "@/lib/categories";
import { editorialTitle, type FeatureCardLook } from "@/lib/home-features";
import { lookPhotoAlt } from "@/lib/photo-alt";

export function HomeFeatureCards({ cards }: { cards: FeatureCardLook[] }) {
  if (cards.length === 0) {
    return null;
  }

  return (
    <section
      aria-labelledby="home-categories-heading"
      data-testid="home-feature-cards"
      className="ky-gutter bg-paper pb-2 pt-8 sm:pb-4 sm:pt-12"
    >
      <div className="mx-auto max-w-7xl">
        <h2
          id="home-categories-heading"
          className="font-display text-[2.15rem] font-medium leading-[1.08] tracking-[0.02em] text-balance text-ink sm:text-[2.75rem]"
          translate="no"
        >
          Categories
        </h2>
        <ul className="mt-6 grid grid-cols-1 gap-5 sm:mt-8 sm:grid-cols-3 sm:gap-8">
          {cards.map((card, index) => (
            <FeatureCard key={card.look.ma} card={card} index={index} />
          ))}
        </ul>
      </div>
    </section>
  );
}

function FeatureCard({ card, index }: { card: FeatureCardLook; index: number }) {
  const ref = useQuietRise<HTMLLIElement>();
  const title = editorialTitle(card.look);
  const category = categoryFilterLabel(card.type);
  const href = `#${categorySectionId(card.type)}`;

  return (
    <li
      ref={ref}
      data-testid="home-feature-card"
      data-ma={card.look.ma}
      className="home-feature-card sc-rise list-none"
      style={{ ["--rise-delay" as string]: `${index * 90}ms` }}
    >
      <Link
        href={href}
        aria-label={categoryAriaLabel(card.type)}
        className="group grid grid-cols-[7.25rem_minmax(0,1fr)] items-center gap-4 touch-manipulation select-none sm:grid-cols-1 sm:items-stretch sm:gap-0"
      >
        <div className="sc-card-well home-feature-photo relative overflow-hidden">
          <ProductImage
            product={card.look}
            alt={lookPhotoAlt({ title, ma: card.look.ma })}
            named={false}
            className="h-full w-full"
            sizes="(max-width: 639px) 30vw, 28vw"
          />
        </div>
        <div className="min-w-0 sm:mt-4 sm:px-0.5">
          <p
            className="text-[11px] font-medium uppercase tracking-[0.16em] text-muted"
            translate="no"
          >
            {category}
          </p>
          <p
            className="mt-1 font-display text-[1.55rem] font-medium leading-[1.08] tracking-[0.02em] text-balance text-ink sm:text-[1.85rem]"
            translate="no"
          >
            {title}
          </p>
        </div>
      </Link>
    </li>
  );
}
