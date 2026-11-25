import { categoryFromSlug } from "@/lib/categories";
import { isOffLiveSell } from "@/lib/held-incomplete";
import { canonicalMaSpelling, isValidMa } from "@/lib/ma";
import { canonicalCategoryPath, canonicalMaPath } from "@/lib/ma-url";

function safeDecode(segment: string): string | null {
  try {
    return decodeURIComponent(segment);
  } catch {
    return null;
  }
}

/**
 * Shop HTML paths that 404 for a reason that does not depend on the live catalog.
 * Held mãs never render. A segment that is not a mã, and a category slug that is
 * not in the fixed list, never render either.
 *
 * A well-formed mã that is not held is not marked here. This seed omits priced
 * looks such as S06, and Blob can list mãs the seed does not. Absence is not
 * proof the page is a 404, so those responses keep the robots meta tag only.
 */
export function isShopHtmlNotFoundPath(pathname: string): boolean {
  const category = pathname.match(/^\/c\/([^/]+)\/?$/);
  if (category) {
    if (canonicalCategoryPath(pathname)) {
      return false;
    }
    const raw = safeDecode(category[1] ?? "");
    if (raw === null) {
      return true;
    }
    return categoryFromSlug(raw.toLowerCase()) === null;
  }

  const ma = pathname.match(/^\/m\/([^/]+)\/?$/);
  if (!ma) {
    return false;
  }
  if (canonicalMaPath(pathname)) {
    return false;
  }
  const raw = safeDecode(ma[1] ?? "");
  if (raw === null) {
    return true;
  }
  const canon = canonicalMaSpelling(raw);
  if (!isValidMa(canon)) {
    return true;
  }
  return isOffLiveSell(canon);
}
