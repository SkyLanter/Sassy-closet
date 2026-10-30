/**
 * Slot width for a look card in the home looks grid and category pages.
 * Columns: 2 below 640px, 3 from 640, 4 from 1024, 5 from 1280.
 * Subtraction is the matching `.ky-gutter` plus `.sc-look-grid` column gaps.
 * The gutter sits outside `max-w-7xl`, so the 5-column slot caps at 84rem
 * (80rem column + 4rem gutter) instead of growing with the viewport.
 * `next/image` turns this into srcset. Remote catalog covers stay a plain
 * `<img>` (see `shouldOptimizeImage`) so a catalog write does not re-encode
 * every photo through the optimizer.
 */
export const LOOK_GRID_SIZES =
  "(max-width: 639px) calc((100vw - 3.25rem) / 2), (max-width: 1023px) calc((100vw - 6.5rem) / 3), (max-width: 1279px) calc((100vw - 7.75rem) / 4), calc((min(100vw, 84rem) - 9rem) / 5)";

/**
 * Related-row cards. Phones use the 70% snap track (capped at 16.5rem).
 * Wider viewports use the same column tracks inside `max-w-7xl`.
 */
export const RELATED_LOOK_SIZES =
  "(max-width: 639px) min(16.5rem, calc((100vw - 2.5rem) * 0.7)), (max-width: 1023px) calc((min(100vw, 80rem) - 6.5rem) / 3), (max-width: 1279px) calc((min(100vw, 80rem) - 7.75rem) / 4), calc((min(100vw, 80rem) - 9rem) / 5)";

/** First above-the-fold covers only. Everything else stays at the browser default and loads lazy. */
export function lookCardFetchPriority(
  priority: boolean,
  explicit?: "high" | "low" | "auto",
): "high" | "low" | "auto" {
  if (explicit) {
    return explicit;
  }
  if (priority) {
    return "high";
  }
  return "auto";
}

export type NativePhotoRead = {
  complete: boolean;
  naturalWidth: number;
  currentSrc: string;
};

export type NativePhotoSettle = "ready" | "broken" | "pending";

/**
 * A native cover can finish before React sees onLoad or onError
 * (the img is in the server HTML, and hydration misses that event).
 * Pixels mean ready. A chosen URL with no pixels is a finished failure.
 * An empty currentSrc has not started, including a lazy image, so it stays pending.
 */
export function nativePhotoSettle(img: NativePhotoRead): NativePhotoSettle {
  if (!img.complete) {
    return "pending";
  }
  if (img.naturalWidth > 0) {
    return "ready";
  }
  if (img.currentSrc) {
    return "broken";
  }
  return "pending";
}

/**
 * Card fades wait until decode, so opacity does not rise on an empty frame.
 * A decode rejection still reveals: the error handler swaps the well if the file failed.
 */
export function revealLookPhoto(
  img: { naturalWidth: number; decode?: () => Promise<void> },
  reveal: () => void,
  fadeIn: boolean,
): void {
  if (img.naturalWidth <= 0) {
    return;
  }
  if (!fadeIn || typeof img.decode !== "function") {
    reveal();
    return;
  }
  img.decode().then(reveal, reveal);
}
