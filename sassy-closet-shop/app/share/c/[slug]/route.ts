import { shareCard } from "@/lib/og-card";
import { categoryShareCardCopy } from "@/lib/share-card";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  context: { params: Promise<{ slug: string }> },
) {
  const { slug } = await context.params;
  return shareCard(categoryShareCardCopy(slug));
}
