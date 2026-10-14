import { ContentWaveHost } from "@/components/content-wave";
import { FeaturedBoard } from "@/components/featured-board";
import { HeroEditorial } from "@/components/hero-mesh";
import { HomeEditorial } from "@/components/home-editorial";
import { firstSearchQueryParam } from "@/lib/look-search";
import { getCatalogTypes, getProducts, getSiteSettings } from "@/lib/products";
import { organizationJsonLd } from "@/lib/seo";
import { SITE } from "@/lib/site";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string | string[] }>;
}) {
  const types = await getCatalogTypes();
  const products = await getProducts();
  const settings = await getSiteSettings();
  const committedQuery = firstSearchQueryParam((await searchParams).q);

  return (
    <div>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd(settings.facebookPageUrl)) }}
      />
      <h1 className="sr-only">{SITE.tagline === SITE.name ? SITE.name : `${SITE.name}. ${SITE.tagline}`}</h1>
      {committedQuery ? null : <HeroEditorial />}
      {committedQuery ? null : <HomeEditorial products={products} types={types} />}
      <ContentWaveHost className="shop-content-layer bg-paper">
        <FeaturedBoard products={products} types={types} committedQuery={committedQuery} />
      </ContentWaveHost>
    </div>
  );
}
