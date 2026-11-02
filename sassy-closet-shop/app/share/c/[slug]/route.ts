import { categoryFromSlug } from "@/lib/categories";
import { renderShareCard } from "@/lib/og-card";
import { coverSrc } from "@/lib/product-media";
import { getProductsByType } from "@/lib/products";
import { categoryShareCardFields } from "@/lib/share-card";
import { shareNotFound, shareUnavailable } from "@/lib/share-card-http";
import { loadSharePhoto } from "@/lib/share-photo";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(
  request: Request,
  context: { params: Promise<{ slug: string }> },
) {
  try {
    const { slug } = await context.params;
    const type = categoryFromSlug(slug);
    if (!type) {
      return shareNotFound();
    }
    const products = await getProductsByType(type);
    const first = products[0];
    const photo = first
      ? await loadSharePhoto(coverSrc(first), { requestUrl: request.url })
      : null;
    return await renderShareCard({
      ...categoryShareCardFields(type, products.length),
      photo,
    });
  } catch (error) {
    console.error("share category card failed", error instanceof Error ? error.message : "error");
    return shareUnavailable();
  }
}
