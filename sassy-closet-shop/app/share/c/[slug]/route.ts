import { categoryFromSlug } from "@/lib/categories";
import { renderShareCard } from "@/lib/og-card";
import { coverSrc } from "@/lib/product-media";
import { getProductsByType } from "@/lib/products";
import { categoryShareCardFields, homeShareCardFields } from "@/lib/share-card";
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
      return new Response("Not found", {
        status: 404,
        headers: { "content-type": "text/plain; charset=utf-8" },
      });
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
    return renderShareCard({ ...homeShareCardFields(), photo: null });
  }
}
