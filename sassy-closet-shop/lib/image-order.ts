import type { ProductImageAsset } from "@/lib/types";

export function reorderImages<T>(images: T[], index: number, direction: -1 | 1): T[] {
  const nextIndex = index + direction;
  if (nextIndex < 0 || nextIndex >= images.length) {
    return images;
  }
  const current = images[index];
  const swap = images[nextIndex];
  if (current === undefined || swap === undefined) {
    return images;
  }
  const next = images.slice();
  next[index] = swap;
  next[nextIndex] = current;
  return next.map((image, orderIndex) => {
    if (typeof image === "object" && image !== null && "order" in image) {
      return { ...image, order: orderIndex + 1 };
    }
    return image;
  });
}

function stampOrders(images: ProductImageAsset[]): ProductImageAsset[] {
  return images.map((image, orderIndex) => ({ ...image, order: orderIndex + 1 }));
}

/** Reorder slides linked to one color (image.colorId) without inventing photos. */
export function moveLinkedSlide(
  images: ProductImageAsset[],
  colorId: string,
  index: number,
  direction: -1 | 1,
): ProductImageAsset[] {
  const positions: number[] = [];
  images.forEach((image, imageIndex) => {
    if (image.colorId === colorId && image.src.trim()) {
      positions.push(imageIndex);
    }
  });
  const from = positions[index];
  const to = positions[index + direction];
  if (from === undefined || to === undefined) {
    return images;
  }
  const current = images[from];
  const swap = images[to];
  if (!current || !swap) {
    return images;
  }
  const next = images.slice();
  next[from] = swap;
  next[to] = current;
  return stampOrders(next);
}

/** Tag an existing unassigned slide to a color, or untag (colorId null). */
export function assignSlideColor(
  images: ProductImageAsset[],
  src: string,
  colorId: string | null,
  currentColorId?: string | null,
): ProductImageAsset[] {
  const target = src.trim();
  if (!target) {
    return images;
  }
  let used = false;
  return stampOrders(
    images.map((image) => {
      if (used || image.src.trim() !== target) {
        return image;
      }
      if (currentColorId !== undefined && image.colorId !== currentColorId) {
        return image;
      }
      used = true;
      return { ...image, colorId };
    }),
  );
}
