import fbMaRank from "@/data/fb-ma-rank.json";
import { compareMa, normalizeMa } from "@/lib/ma";
import type { Product } from "@/lib/types";

export const DEFAULT_SHOP_SORT = "popular" as const;

export type ShopSortId = "popular" | "ma" | "price-asc" | "price-desc";

export type FbMaRankRow = {
  rank: number;
  ma: string;
  views: number;
  engagement: number;
  fbPosts: number;
};

type FbMaRankFile = {
  source: string;
  window: string;
  sortKey: string;
  unrankedSecondary: "ma";
  rows: FbMaRankRow[];
};

const RANK_FILE = fbMaRank as FbMaRankFile;

const RANK_BY_MA = new Map<string, FbMaRankRow>(
  RANK_FILE.rows.map((row) => [normalizeMa(row.ma), row]),
);

/** Authoritative aggregated FB rank. Unranked mãs have no row. */
export function fbRankRow(ma: string): FbMaRankRow | undefined {
  return RANK_BY_MA.get(normalizeMa(ma));
}

export function fbRankOf(ma: string): number | undefined {
  return fbRankRow(ma)?.rank;
}

export function fbRankTable(): readonly FbMaRankRow[] {
  return RANK_FILE.rows;
}

export function fbRankSourceNote(): string {
  return `${RANK_FILE.source} (${RANK_FILE.window}; ${RANK_FILE.sortKey}). Unranked mãs sort after ranked ones by ${RANK_FILE.unrankedSecondary}.`;
}

/**
 * Stamp CSV rank onto a catalog mã. Does not invent mãs, prices, or photos.
 * Mãs missing from the ranking table keep no FB fields.
 */
export function applyFbRank(product: Product): Product {
  const row = fbRankRow(product.ma);
  if (!row) {
    return {
      ...product,
      fbRank: undefined,
      fbViews: undefined,
      fbEngagement: undefined,
      fbPosts: undefined,
    };
  }
  return {
    ...product,
    fbRank: row.rank,
    fbViews: row.views,
    fbEngagement: row.engagement,
    fbPosts: row.fbPosts,
  };
}

export function applyFbRankToCatalog(products: Product[]): Product[] {
  return products.map(applyFbRank);
}

/**
 * Popular: CSV rank (views DESC, engagement DESC), then mã.
 * Unranked mãs (no FB post in the 90-day table) sort after every ranked mã, by mã.
 */
export function compareByPopularThenMa(leftMa: string, rightMa: string): number {
  const leftRank = fbRankOf(leftMa) ?? Number.POSITIVE_INFINITY;
  const rightRank = fbRankOf(rightMa) ?? Number.POSITIVE_INFINITY;
  if (leftRank !== rightRank) {
    return leftRank - rightRank;
  }
  return compareMa(leftMa, rightMa);
}

export function sortProductsByPopular<T extends { ma: string }>(items: T[]): T[] {
  return [...items].sort((left, right) => compareByPopularThenMa(left.ma, right.ma));
}

export function sortByMa<T extends { ma: string }>(items: T[]): T[] {
  return [...items].sort((left, right) => compareMa(left.ma, right.ma));
}

export function sortShopLooks<T extends { ma: string }>(items: T[], sort: ShopSortId): T[] {
  switch (sort) {
    case "popular":
      return sortProductsByPopular(items);
    case "ma":
      return sortByMa(items);
    default: {
      const _exhaustive: never = sort;
      return _exhaustive;
    }
  }
}

export const SHOP_SORT_OPTIONS: ReadonlyArray<{
  id: ShopSortId;
  label: string;
  aria: string;
}> = [
  { id: "popular", label: "Popular", aria: "Popular · Most viewed" },
  { id: "ma", label: "Mã", aria: "Mã A to Z" },
];
