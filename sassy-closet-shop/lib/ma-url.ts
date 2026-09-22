import { categoryFromSlug } from "@/lib/categories";
import { isValidMa, normalizeMa } from "@/lib/ma";

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

/** `/c/Ao` → `/c/ao`. Null when already lowercase or unknown. */
export function canonicalCategoryPath(pathname: string): string | null {
  const match = pathname.match(/^\/c\/([^/]+)\/?$/);
  if (!match) {
    return null;
  }
  const raw = decodeURIComponent(match[1] ?? "");
  const lower = raw.toLowerCase();
  if (raw === lower || !categoryFromSlug(lower)) {
    return null;
  }
  return `/c/${lower}`;
}
