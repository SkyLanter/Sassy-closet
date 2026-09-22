import { ContentWaveHost } from "@/components/content-wave";
import { FeaturedBoard } from "@/components/featured-board";
import { HeroEditorial } from "@/components/hero-mesh";
import { firstSearchQueryParam } from "@/lib/look-search";
import { getCatalogTypes, getProducts, getSiteSettings } from "@/lib/products";
import { organizationJsonLd } from "@/lib/seo";

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
      <HeroEditorial />
      <ContentWaveHost className="shop-content-layer bg-paper">
        <FeaturedBoard products={products} types={types} committedQuery={committedQuery} />
      </ContentWaveHost>
    </div>
  );
}
