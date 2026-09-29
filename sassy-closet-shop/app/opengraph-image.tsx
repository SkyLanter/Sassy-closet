import { renderShareCard } from "@/lib/og-card";
import { coverSrc } from "@/lib/product-media";
import { getProduct } from "@/lib/products";
import { homeShareCardFields } from "@/lib/share-card";
import { loadSharePhoto } from "@/lib/share-photo";

export const alt = "Sassy Closet lookbook";
export const size = { width: 1200, height: 630 };
export const contentType = "image/jpeg";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export default async function OpengraphImage() {
  try {
    const cover = await getProduct("D02");
    const photo = cover ? await loadSharePhoto(coverSrc(cover)) : null;
    return await renderShareCard({ ...homeShareCardFields(), photo });
  } catch (error) {
    console.error("home share card failed", error instanceof Error ? error.message : "error");
    return renderShareCard({ ...homeShareCardFields(), photo: null });
  }
}
