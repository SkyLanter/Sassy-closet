import { categorySearchLabels } from "@/lib/categories";
import { isValidMa, maLetter, normalizeMa } from "@/lib/ma";

/** Customer search index — mã + titles only. Never invent rows. */
export type LookSearchItem = {
  ma: string;
  titleEn: string;
  titleVn: string;
};

export const LOOK_SEARCH_PLACEHOLDER = "Tìm mã (A15)… / Search mã";
export const LOOK_SEARCH_ARIA = "Tìm mã hoặc tên · Search mã or name";
export const LOOK_SEARCH_EMPTY = "Không thấy look · No matching look";
export const LOOK_SEARCH_TOGGLE = "Mở tìm · Open search";
export const LOOK_SEARCH_CLOSE = "Đóng tìm · Close search";
export const LOOK_SEARCH_NO_MATCH = "Không thấy mã hoặc tên đó · No look matches that search.";
export const LOOK_SEARCH_TAB_EMPTY = "Không có trong mục này · Nothing in this tab matches.";

/** Keys this shop does not write today. Home still clears them so a stuck filter cannot survive in storage. */
export const SHOP_SEARCH_STORAGE_KEYS = ["sassy-shop-search", "sassy-shop-q"] as const;

/**
 * Home URL is the filter. `null` means we left home and the header may keep its text.
 * `""` means `/` has no q, so a previous mã must not keep filtering.
 */
export function draftAfterHomeQuery(homeQuery: string | null, draft: string | null): string | null {
  if (homeQuery === null) {
    return draft;
  }
  return homeQuery.trim();
}

/** `""` is an explicit clear and beats a stale `?q`. `null` follows the URL query. */
export function shopSearchNeedle(draft: string | null, committedQuery: string): string {
  if (draft === null) {
    return committedQuery.trim();
  }
  return draft.trim();
}

/** ASCII request header so a unicode query can survive the proxy. */
export const SHOP_SEARCH_HEADER = "x-sassy-q";

const SHOP_SEARCH_MAX = 80;

export function encodeShopSearchHeader(query: string): string {
  return encodeURIComponent(query.trim().slice(0, SHOP_SEARCH_MAX));
}

/**
 * Header search submit payload for Web Analytics.
 * Trimmed, capped at 80 characters. Blank queries are not events.
 */
export function searchSubmitQuery(raw: string): string | null {
  const query = raw.trim().slice(0, SHOP_SEARCH_MAX);
  if (!query) {
    return null;
  }
  return query;
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

/** Fold accents, map đ → d, and collapse whitespace. Shared by haystack and needle. */
export function foldSearchText(value: string): string {
  const folded = value.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();
  return folded.replace(/đ/g, "d").replace(/\s+/g, " ").trim();
}

function categoryText(ma: string): string {
  const letter = maLetter(ma);
  if (!letter) {
    return "";
  }
  return categorySearchLabels(letter);
}

export function lookSearchHaystack(look: LookSearchItem): string {
  return foldSearchText(`${look.ma} ${look.titleEn} ${look.titleVn} ${categoryText(look.ma)}`);
}

const LOOSE_MA = /^([a-z])[\s-]*(\d+)$/i;

/**
 * A whole query that is one letter, optional spaces or dashes, then digits.
 * Leading zeros stay (`a015` → A015) so they cannot become a different mã.
 */
export function looseMaCandidate(query: string): string | null {
  const match = query.trim().match(LOOSE_MA);
  const letter = match?.[1];
  const digits = match?.[2];
  if (!letter || !digits) {
    return null;
  }
  const ma = `${letter.toUpperCase()}${digits}`;
  return isValidMa(ma) ? ma : null;
}

function stemMatches(haystack: string, token: string): boolean {
  if (haystack.includes(token)) {
    return true;
  }
  if (token.length > 3 && token.endsWith("s") && !token.endsWith("ss")) {
    const stem = token.slice(0, -1);
    if (stem.length >= 3 && haystack.includes(stem)) {
      return true;
    }
  }
  if (token.length > 4 && token.endsWith("es")) {
    const stem = token.slice(0, -2);
    if (stem.length >= 3 && haystack.includes(stem)) {
      return true;
    }
  }
  return false;
}

export function filterLooksByQuery<T extends LookSearchItem>(
  looks: T[],
  query: string,
): T[] {
  const raw = query.trim();
  if (!raw) {
    return looks;
  }
  const ma = looseMaCandidate(raw);
  if (ma) {
    const hit = looks.find((look) => look.ma === ma);
    if (hit) {
      return [hit];
    }
  }
  // A partial mã (`a1`, `d0`, `a 1`) is not an exact row. Match the prefix
  // with spaces and dashes removed so typing A15 one key at a time still lists looks.
  const needle = ma ? raw.replace(/[\s-]+/g, "") : raw;
  const tokens = foldSearchText(needle).split(" ").filter(Boolean);
  if (tokens.length === 0) {
    return looks;
  }
  return looks.filter((look) => {
    const haystack = lookSearchHaystack(look);
    return tokens.every((token) => stemMatches(haystack, token));
  });
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
  const candidate = isValidMa(normalized) ? normalized : looseMaCandidate(query);
  if (!candidate || !isValidMa(candidate)) {
    return undefined;
  }
  return looks.find((look) => look.ma === candidate);
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
