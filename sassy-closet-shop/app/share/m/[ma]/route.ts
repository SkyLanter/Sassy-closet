import { getProduct } from "@/lib/products";
import { shareCard } from "@/lib/og-card";
import { productShareCardCopy } from "@/lib/share-card";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  context: { params: Promise<{ ma: string }> },
) {
  const { ma } = await context.params;
  const product = await getProduct(ma);
  return shareCard(productShareCardCopy(product, ma));
}
