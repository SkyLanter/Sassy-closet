import { categoryFromSlug } from "@/lib/categories";
import { isOffLiveSell } from "@/lib/held-incomplete";
import { canonicalMaSpelling, isValidMa } from "@/lib/ma";

/**
 * Old Hair slug from before the category was `toc`.
 * Accessories stay `phu-kien`. Do not add other aliases.
 */
const STALE_CATEGORY_SLUGS: Readonly<Record<string, string>> = {
  "phu-kien-toc": "toc",
};

function safeDecode(segment: string): string | null {
  try {
    return decodeURIComponent(segment);
  } catch {
    return null;
  }
}

/** Canonical mã for a redirect, or null when the segment is already that spelling. */
function redirectSpelling(raw: string | null): string | null {
  if (raw === null) {
    return null;
  }
  const canon = canonicalMaSpelling(raw);
  if (!isValidMa(canon) || raw === canon) {
    return null;
  }
  return canon;
}

/**
 * `/m/a01`, `/m/A001`, `/m/a1` → `/m/A01`.
 * `/products/a1/cover.jpg` → `/products/A01/cover.jpg`.
 * Null when already canonical or not a mã path.
 */
export function canonicalMaPath(pathname: string): string | null {
  const maPage = pathname.match(/^((?:\/share)?)\/m\/([^/]+)(\/.*)?$/);
  if (maPage) {
    const canon = redirectSpelling(safeDecode(maPage[2] ?? ""));
    if (!canon) {
      return null;
    }
    const prefix = maPage[1] ?? "";
    const rest = maPage[3] ?? "";
    return `${prefix}/m/${canon}${rest}`;
  }
  const photo = pathname.match(/^\/products\/([^/]+)(\/.*)?$/);
  if (!photo) {
    return null;
  }
  const canon = redirectSpelling(safeDecode(photo[1] ?? ""));
  // A held spelling must not 308 onto public/products/{mã}, which Next serves
  // before the image route can 404.
  if (!canon || isOffLiveSell(canon)) {
    return null;
  }
  const rest = photo[2] ?? "";
  return `/products/${canon}${rest}`;
}

/**
 * `/c/Ao` → `/c/ao`. `/c/phu-kien-toc` → `/c/toc`.
 * Same for `/share/c/…`. Null when already canonical or unknown.
 */
export function canonicalCategoryPath(pathname: string): string | null {
  const match = pathname.match(/^((?:\/share)?)\/c\/([^/]+)\/?$/);
  if (!match) {
    return null;
  }
  const prefix = match[1] ?? "";
  const raw = safeDecode(match[2] ?? "");
  if (raw === null) {
    return null;
  }
  const lower = raw.toLowerCase();
  const stale = STALE_CATEGORY_SLUGS[lower];
  if (stale) {
    return `${prefix}/c/${stale}`;
  }
  if (raw === lower || !categoryFromSlug(lower)) {
    return null;
  }
  return `${prefix}/c/${lower}`;
}
