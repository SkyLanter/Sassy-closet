/**
 * Slot width for a look card in the home looks grid and category pages.
 * Columns: 2 below 640px, 3 from 640, 4 from 1024, 5 from 1280.
 * Subtraction is the matching `.ky-gutter` plus `.sc-look-grid` column gaps.
 * `next/image` turns this into srcset. Remote catalog covers stay a plain
 * `<img>` (see `shouldOptimizeImage`) so a catalog write does not re-encode
 * every photo through the optimizer.
 */
export const LOOK_GRID_SIZES =
  "(max-width: 639px) calc((100vw - 3.25rem) / 2), (max-width: 1023px) calc((100vw - 6.5rem) / 3), (max-width: 1279px) calc((100vw - 7.75rem) / 4), calc((100vw - 9rem) / 5)";

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
