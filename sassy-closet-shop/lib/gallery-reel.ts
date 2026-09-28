import { colorShopLabel } from "@/lib/colors";
import { lookPhotoAlt } from "@/lib/photo-alt";
import { ownMaImages, type MaMedia } from "@/lib/product-media";
import type { ProductImageAsset } from "@/lib/types";

type ReelSource = MaMedia & { titleEn?: string; titleVn?: string };

function reelAlt(product: ReelSource, color: string | null, index: number): string {
  const title = (product.titleEn?.trim() || product.titleVn?.trim() || product.ma).toUpperCase();
  return lookPhotoAlt({ title, ma: product.ma, color, index });
}

export type GalleryReelSlide = {
  id: string;
  src: string;
  alt: string;
  role: "photo" | "hint";
  colorId: string | null;
  colorName?: string;
  photoIndex: number;
};

function usableImages(product: MaMedia): ProductImageAsset[] {
  return ownMaImages(product);
}

/** One watery reel of unique photos. Never clone the same JPEG as a fake neighbor. */
export function productGalleryReel(product: ReelSource): GalleryReelSlide[] {
  const usable = usableImages(product);
  if (usable.length === 0) {
    return [];
  }

  if (product.colors.length === 0) {
    return usable.map((image, photoIndex) => ({
      id: `all-${photoIndex}-${image.src}`,
      src: image.src,
      alt: reelAlt(product, null, photoIndex + 1),
      role: "photo" as const,
      colorId: null,
      photoIndex,
    }));
  }

  const slides: GalleryReelSlide[] = [];
  const seen = new Set<string>();

  product.colors.forEach((color, colorIndex) => {
    const name = colorShopLabel(color, colorIndex);
    const tagged = usable.filter((image) => image.colorId === color.id);
    tagged.forEach((image, photoIndex) => {
      if (seen.has(image.src)) {
        return;
      }
      seen.add(image.src);
      slides.push({
        id: `${color.id}-${photoIndex}-${image.src}`,
        src: image.src,
        alt: reelAlt(product, name, photoIndex + 1),
        role: "photo",
        colorId: color.id,
        colorName: name,
        photoIndex,
      });
    });
  });

  usable
    .filter((image) => image.colorId === null)
    .forEach((image, photoIndex) => {
      if (seen.has(image.src)) {
        return;
      }
      seen.add(image.src);
      slides.push({
        id: `shared-${photoIndex}-${image.src}`,
        src: image.src,
        alt: reelAlt(product, null, photoIndex + 1),
        role: "photo",
        colorId: null,
        photoIndex,
      });
    });

  usable.forEach((image, photoIndex) => {
    if (seen.has(image.src)) {
      return;
    }
    seen.add(image.src);
    slides.push({
      id: `rest-${photoIndex}-${image.src}`,
      src: image.src,
      alt: reelAlt(product, null, photoIndex + 1),
      role: "photo",
      colorId: image.colorId,
      photoIndex,
    });
  });

  return slides;
}

/** First reel index for a chip. Tagged slide, else shared `null`. `-1` = this color has no photos — chip only, do not steal another finish’s JPEG. */
export function firstReelIndexForColor(
  slides: GalleryReelSlide[],
  colorId: string | null,
): number {
  if (colorId === null) {
    return 0;
  }
  const tagged = slides.findIndex((slide) => slide.colorId === colorId);
  if (tagged >= 0) {
    return tagged;
  }
  const shared = slides.findIndex((slide) => slide.colorId === null);
  return shared;
}

export function clampedReelIndexForColor(
  slides: GalleryReelSlide[],
  colorId: string | null,
): number {
  if (slides.length === 0) {
    return 0;
  }
  const target = firstReelIndexForColor(slides, colorId);
  if (target < 0) {
    return 0;
  }
  return target;
}
