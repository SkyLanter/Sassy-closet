import { coverSrc } from "@/lib/product-media";
import { PRIVATE_NOT_FOUND_HEADERS } from "@/lib/private-robots";
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
        headers: PRIVATE_NOT_FOUND_HEADERS,
      });
    }
    const photo = await loadSharePhoto(coverSrc(product), { requestUrl: request.url });
    return await renderShareCard({ ...productShareCardCopy(product), photo });
  } catch (error) {
    console.error("share product card failed", error instanceof Error ? error.message : "error");
    return renderShareCard({ ...homeShareCardFields(), photo: null });
  }
}
