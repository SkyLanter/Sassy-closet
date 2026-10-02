import { categoryFromSlug } from "@/lib/categories";
import { isValidMa, normalizeMa } from "@/lib/ma";

/**
 * Old Hair slug from before the category was `toc`.
 * Accessories stay `phu-kien`. Do not add other aliases.
 */
const STALE_CATEGORY_SLUGS: Readonly<Record<string, string>> = {
  "phu-kien-toc": "toc",
};

/** `/m/a01` → `/m/A01`. Null when already canonical or not a mã path. */
export function canonicalMaPath(pathname: string): string | null {
  const match = pathname.match(/^((?:\/share)?)\/m\/([^/]+)(\/.*)?$/);
  if (!match) {
    return null;
  }
  const prefix = match[1] ?? "";
  const raw = decodeURIComponent(match[2] ?? "");
  const rest = match[3] ?? "";
  const canon = normalizeMa(raw);
  if (!isValidMa(canon) || raw === canon) {
    return null;
  }
  return `${prefix}/m/${canon}${rest}`;
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
  const raw = decodeURIComponent(match[2] ?? "");
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
