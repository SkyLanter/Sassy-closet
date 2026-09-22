import { isValidMa, normalizeMa } from "@/lib/ma";

/** Customer search index — mã + titles only. Never invent rows. */
export type LookSearchItem = {
  ma: string;
  titleEn: string;
  titleVn: string;
};

export const LOOK_SEARCH_PLACEHOLDER = "Tìm mã hoặc tên…";
export const LOOK_SEARCH_ARIA = "Tìm mã hoặc tên · Search mã or name";
export const LOOK_SEARCH_EMPTY = "Không thấy look · No matching look";
export const LOOK_SEARCH_TOGGLE = "Mở tìm · Open search";
export const LOOK_SEARCH_CLOSE = "Đóng tìm · Close search";
export const LOOK_SEARCH_NO_MATCH = "Không thấy mã hoặc tên đó · No look matches that search.";
export const LOOK_SEARCH_TAB_EMPTY = "Không có trong mục này · Nothing in this tab matches.";

/** ASCII request header so a unicode query can survive the proxy. */
export const SHOP_SEARCH_HEADER = "x-sassy-q";

const SHOP_SEARCH_MAX = 80;

export function encodeShopSearchHeader(query: string): string {
  return encodeURIComponent(query.trim().slice(0, SHOP_SEARCH_MAX));
}

export function decodeShopSearchHeader(raw: string | null): string {
  if (!raw) {
    return "";
  }
  try {
    return decodeURIComponent(raw).trim().slice(0, SHOP_SEARCH_MAX);
  } catch {
    return "";
  }
}

const SUGGESTION_LIMIT = 8;

export function toLookSearchItems(
  looks: Array<LookSearchItem>,
): LookSearchItem[] {
  return looks.map((look) => ({
    ma: look.ma,
    titleEn: look.titleEn,
    titleVn: look.titleVn,
  }));
}

export function firstSearchQueryParam(
  value: string | string[] | undefined,
): string {
  if (Array.isArray(value)) {
    return value[0]?.trim() ?? "";
  }
  return value?.trim() ?? "";
}

export function lookSearchHaystack(look: LookSearchItem): string {
  return `${look.ma} ${look.titleEn} ${look.titleVn}`.toLowerCase();
}

export function filterLooksByQuery<T extends LookSearchItem>(
  looks: T[],
  query: string,
): T[] {
  const needle = query.trim().toLowerCase();
  if (!needle) {
    return looks;
  }
  return looks.filter((look) => lookSearchHaystack(look).includes(needle));
}

export function suggestLooks<T extends LookSearchItem>(
  looks: T[],
  query: string,
): T[] {
  const needle = query.trim();
  if (!needle) {
    return [];
  }
  return filterLooksByQuery(looks, needle).slice(0, SUGGESTION_LIMIT);
}

/** Exact mã only when that mã already exists on the lookbook. */
export function exactMaLook<T extends LookSearchItem>(
  looks: T[],
  query: string,
): T | undefined {
  const normalized = normalizeMa(query);
  if (!isValidMa(normalized)) {
    return undefined;
  }
  return looks.find((look) => look.ma === normalized);
}

export type LookSearchResolution =
  | { kind: "exact"; ma: string }
  | { kind: "results"; query: string };

export function resolveLookSearch(
  looks: LookSearchItem[],
  raw: string,
): LookSearchResolution {
  const query = raw.trim();
  const exact = exactMaLook(looks, query);
  if (exact) {
    return { kind: "exact", ma: exact.ma };
  }
  return { kind: "results", query };
}

export function lookSearchHref(resolution: LookSearchResolution): string {
  switch (resolution.kind) {
    case "exact":
      return `/m/${resolution.ma}`;
    case "results":
      return resolution.query
        ? `/?q=${encodeURIComponent(resolution.query)}#featured-collection`
        : "/#featured-collection";
    default: {
      const _exhaustive: never = resolution;
      return _exhaustive;
    }
  }
}
