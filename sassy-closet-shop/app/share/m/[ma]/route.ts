import { coverSrc } from "@/lib/product-media";
import { getProduct } from "@/lib/products";
import { renderShareCard } from "@/lib/og-card";
import { homeShareCardFields, productShareCardCopy } from "@/lib/share-card";
import { loadSharePhoto } from "@/lib/share-photo";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(
  request: Request,
  context: { params: Promise<{ ma: string }> },
) {
  try {
    const { ma } = await context.params;
    const product = await getProduct(ma);
    if (!product) {
      return new Response("Not found", {
        status: 404,
        headers: { "content-type": "text/plain; charset=utf-8" },
      });
    }
    const photo = await loadSharePhoto(coverSrc(product), { requestUrl: request.url });
    return await renderShareCard({ ...productShareCardCopy(product), photo });
  } catch (error) {
    console.error("share product card failed", error instanceof Error ? error.message : "error");
    return renderShareCard({ ...homeShareCardFields(), photo: null });
  }
}
