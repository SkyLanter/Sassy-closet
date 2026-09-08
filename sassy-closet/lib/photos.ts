export const FIND_CARD_THUMB_LIMIT = 3;

export function realPhotoPaths(paths: unknown): string[] {
  if (!Array.isArray(paths)) return [];
  const out: string[] = [];
  for (const item of paths) {
    if (typeof item !== "string") continue;
    const trimmed = item.trim();
    if (trimmed) out.push(trimmed);
  }
  return out;
}

export function photoSrc(pathOrUrl: string): string {
  const value = pathOrUrl.trim();
  if (!value) return "";
  if (
    value.startsWith("blob:") ||
    value.startsWith("data:") ||
    value.startsWith("http://") ||
    value.startsWith("https://") ||
    value.startsWith("/")
  ) {
    return value;
  }
  return `/api/photos/${value.replace(/^\/+/, "")}`;
}

export function visiblePhotoPaths(
  paths: unknown,
  limit = FIND_CARD_THUMB_LIMIT,
): { all: string[]; shown: string[]; extra: number } {
  const all = realPhotoPaths(paths);
  if (!Number.isFinite(limit) || limit < 0) {
    return { all, shown: all, extra: 0 };
  }
  const shown = all.slice(0, limit);
  return { all, shown, extra: Math.max(0, all.length - shown.length) };
}
