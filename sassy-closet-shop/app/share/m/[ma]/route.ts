import { coverSrc } from "@/lib/product-media";
import { getProduct } from "@/lib/products";
import { renderShareCard } from "@/lib/og-card";
import { productShareCardCopy } from "@/lib/share-card";
import { shareNotFound, shareUnavailable } from "@/lib/share-card-http";
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
      return shareNotFound();
    }
    const photo = await loadSharePhoto(coverSrc(product), { requestUrl: request.url });
    return await renderShareCard({ ...productShareCardCopy(product), photo });
  } catch (error) {
    console.error("share product card failed", error instanceof Error ? error.message : "error");
    return shareUnavailable();
  }
}
