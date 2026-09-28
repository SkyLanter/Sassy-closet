export type LockedBossStatus = "available" | "hold" | "sold";

export type LockedBossPrice = {
  ma: string;
  priceUsd: number | null;
  status: LockedBossStatus;
};

/**
 * Same rows as sassy-closet-shop `BOSS_PRICE_LIST`.
 * Shop reads still apply `presentLockedBossPrices`. This list only stops
 * the intake desk from writing a different price or status for those mãs.
 */
export const LOCKED_BOSS_PRICES: readonly LockedBossPrice[] = [
  { ma: "A01", priceUsd: 25, status: "available" },
  { ma: "S01", priceUsd: 39, status: "available" },
  { ma: "P01", priceUsd: 5, status: "available" },
  { ma: "P02", priceUsd: 24, status: "available" },
  { ma: "P03", priceUsd: 10, status: "available" },
  { ma: "P04", priceUsd: 9, status: "available" },
  { ma: "P05", priceUsd: 23, status: "available" },
  { ma: "K01", priceUsd: 36, status: "available" },
  { ma: "H01", priceUsd: 8, status: "available" },
  { ma: "A02", priceUsd: 21, status: "available" },
];

export function lockedBossPrice(ma: string): LockedBossPrice | undefined {
  return LOCKED_BOSS_PRICES.find((row) => row.ma === ma);
}
