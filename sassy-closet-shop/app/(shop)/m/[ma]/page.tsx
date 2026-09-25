import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { BuyBar } from "@/components/buy-bar";
import { ContentWaveHost, ContentWaveLooks } from "@/components/content-wave";
import { ProductLook } from "@/components/product-look";
import { ProductGrid } from "@/components/product-grid";
import { categoryAriaLabel, categoryCopy } from "@/lib/categories";
import { lookCountLabel } from "@/lib/look-count";
import { KNOWN_SEED_MAS } from "@/lib/catalog-contract";
import { getProduct, getProductsByType } from "@/lib/products";
import { productJsonLd, productSeo } from "@/lib/seo";

export const dynamic = "force-dynamic";
export const dynamicParams = true;
export const revalidate = 0;

export function generateStaticParams() {
  return KNOWN_SEED_MAS.map((ma) => ({ ma }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ ma: string }>;
}): Promise<Metadata> {
  const { ma } = await params;
  const product = await getProduct(ma);
  if (!product) {
    return { title: "Item not found" };
  }
  return productSeo(product);
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ ma: string }>;
}) {
  const { ma } = await params;
  const product = await getProduct(ma);
  if (!product) {
    notFound();
  }

  const type = categoryCopy(product.type);
  const related = (await getProductsByType(product.type)).filter((item) => item.ma !== product.ma);

  return (
    <div className="bg-paper">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(productJsonLd(product)) }}
      />
      <ContentWaveHost className="shop-content-layer">
        <ProductLook product={product} />

        {related.length > 0 ? (
          <section className="ky-section-film" aria-labelledby="related-heading">
            <div className="mx-auto max-w-7xl ky-gutter py-10 sm:py-12">
              <h2
                id="related-heading"
                aria-label={categoryAriaLabel(product.type)}
                className="scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)] text-left font-display text-[1.85rem] font-medium leading-[1.08] tracking-[0.03em] text-balance text-ink outline-none sm:scroll-mt-[calc(env(safe-area-inset-top,0px)+8.75rem)] sm:text-4xl"
                translate="no"
              >
                {type.label}
              </h2>
              <p className="mx-auto mt-2 max-w-full truncate whitespace-nowrap text-left text-[11px] uppercase tracking-[0.16em] text-muted tabular-nums" translate="no">
                {lookCountLabel(related.length, true)}
              </p>
              <div className="mt-8">
                <ContentWaveLooks>
                  <ProductGrid products={related} />
                </ContentWaveLooks>
              </div>
            </div>
          </section>
        ) : null}
      </ContentWaveHost>

      <BuyBar product={product} />
    </div>
  );
}
