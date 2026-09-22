import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ContentWaveHost } from "@/components/content-wave";
import { LooksCatalog } from "@/components/looks-catalog";
import { ShopEmpty } from "@/components/shop-empty";
import { categoryAriaLabel, categoryCopy, categoryFromSlug, TYPE_SLUGS } from "@/lib/categories";
import { collectionEmptyCopy, lookCountLabel } from "@/lib/look-count";
import { getProductsByType } from "@/lib/products";
import { categoryJsonLd, categorySeo } from "@/lib/seo";

export const dynamic = "force-dynamic";
export const dynamicParams = true;
export const revalidate = 0;

export function generateStaticParams() {
  return Object.values(TYPE_SLUGS).map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const type = categoryFromSlug(slug);
  if (!type) {
    notFound();
  }
  return categorySeo(type);
}

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const type = categoryFromSlug(slug);
  if (!type) {
    notFound();
  }

  const labels = categoryCopy(type);
  const products = await getProductsByType(type);
  const jsonLd = categoryJsonLd(labels.label, slug, products);
  const countLabel = lookCountLabel(products.length);

  return (
    <ContentWaveHost className="shop-content-layer bg-paper ky-gutter py-10 sm:py-12 scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)] sm:scroll-mt-[calc(env(safe-area-inset-top,0px)+8.75rem)]">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="mx-auto max-w-7xl">
        <h1
          aria-label={categoryAriaLabel(type)}
          className="text-left font-display text-[2.15rem] font-medium leading-[1.08] tracking-[0.02em] text-balance text-ink outline-none sm:text-[2.75rem]"
          translate="no"
        >
          {labels.label}
        </h1>
        <p
          className="mx-auto mt-3 max-w-full truncate whitespace-nowrap text-left text-[11px] uppercase tracking-[0.16em] text-muted tabular-nums"
          aria-live="polite"
          translate="no"
        >
          {countLabel}
        </p>
        {products.length === 0 ? (
          <div className="mt-10">
            <ShopEmpty {...collectionEmptyCopy(labels.label, slug)} />
          </div>
        ) : (
          <LooksCatalog products={products} motionKey={slug} />
        )}
      </div>
    </ContentWaveHost>
  );
}
