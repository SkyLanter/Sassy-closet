import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { CategoryLandingScroll } from "@/components/category-landing-scroll";
import { ContentWaveHost } from "@/components/content-wave";
import { FeaturedBoard } from "@/components/featured-board";
import { categoryAriaLabel, categoryCopy, categoryFromSlug, categorySectionId, TYPE_SLUGS } from "@/lib/categories";
import { getCatalogTypes, getProducts } from "@/lib/products";
import { categoryJsonLd, categorySeo, notFoundSeo } from "@/lib/seo";

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
    return notFoundSeo();
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
  const products = await getProducts();
  const types = await getCatalogTypes();
  const inCategory = products.filter((product) => product.type === type);
  const jsonLd = categoryJsonLd(labels.label, slug, inCategory);

  return (
    <ContentWaveHost className="shop-content-layer bg-paper scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)] sm:scroll-mt-[calc(env(safe-area-inset-top,0px)+8.75rem)]">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <h1
        aria-label={categoryAriaLabel(type)}
        className="sr-only truncate whitespace-nowrap text-left font-display text-[2.15rem] font-medium leading-[1.08] tracking-[0.02em] text-balance text-ink outline-none"
        translate="no"
      >
        {labels.label}
      </h1>
      <CategoryLandingScroll sectionId={categorySectionId(type)} />
      <FeaturedBoard products={products} types={types} landingType={type} />
    </ContentWaveHost>
  );
}
