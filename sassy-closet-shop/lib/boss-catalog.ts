import { KNOWN_SEED_MAS, type KnownSeedMa } from "@/lib/catalog-contract";
import type { Product, ProductStatus } from "@/lib/types";

export type BossPriceRow = {
  ma: KnownSeedMa;
  priceUsd: number | null;
  status: ProductStatus;
};

/**
 * Boss-locked sell prices (25% margin, 2026-09-28).
 * price = ceil(landed / 0.75); if that result is under $10, add $2.
 * Do not invent mãs or USD. Hold has no price.
 */
export const BOSS_PRICE_LIST: readonly BossPriceRow[] = [
  { ma: "A01", priceUsd: 24, status: "available" },
  { ma: "S01", priceUsd: 37, status: "available" },
  { ma: "P01", priceUsd: 5, status: "available" },
  { ma: "P02", priceUsd: 22, status: "available" },
  { ma: "P03", priceUsd: 10, status: "available" },
  { ma: "P04", priceUsd: 9, status: "available" },
  { ma: "P05", priceUsd: 22, status: "available" },
  { ma: "K01", priceUsd: 34, status: "available" },
  { ma: "H01", priceUsd: 7, status: "available" },
  { ma: "A02", priceUsd: 20, status: "available" },
] as const;

/**
 * Prices still stored on the live Blob for the seven repriced locks.
 * The catalog patch lands at merge time. Until then these values are not corrupt:
 * the lock is what the shop publishes.
 */
const PREVIOUS_BOSS_PRICE_USD: Partial<Record<KnownSeedMa, number>> = {
  A01: 25,
  A02: 21,
  S01: 39,
  K01: 36,
  H01: 8,
  P02: 24,
  P05: 23,
};

const warnedBossPriceLag = new Set<string>();

export function previousBossPriceUsd(ma: string): number | undefined {
  if (!Object.prototype.hasOwnProperty.call(PREVIOUS_BOSS_PRICE_USD, ma)) {
    return undefined;
  }
  return PREVIOUS_BOSS_PRICE_USD[ma as KnownSeedMa];
}

export function resetBossPriceLagWarnings(): void {
  warnedBossPriceLag.clear();
}

export function warnBossPriceLag(ma: string, storedUsd: number | null, lockUsd: number): void {
  const key = `${ma}:${String(storedUsd)}`;
  if (warnedBossPriceLag.has(key)) {
    return;
  }
  warnedBossPriceLag.add(key);
  console.warn(
    `Mã ${ma} catalog price $${String(storedUsd)} differs from Boss lock $${lockUsd}. Publishing the lock until catalog.v1.json is patched.`,
  );
}

export function bossRow(ma: string): BossPriceRow | undefined {
  return BOSS_PRICE_LIST.find((row) => row.ma === ma);
}

export function assertBossPrices(products: Product[]): void {
  const byMa = new Map(products.map((product) => [product.ma, product]));
  for (const ma of KNOWN_SEED_MAS) {
    const product = byMa.get(ma);
    const row = bossRow(ma);
    if (!product || !row) {
      throw new Error(`Missing locked mã ${ma}`);
    }
    if (product.status !== row.status) {
      throw new Error(`Mã ${ma} status must be ${row.status} in seed (got ${product.status})`);
    }
    if (product.priceUsd !== row.priceUsd) {
      throw new Error(`Mã ${ma} price must be ${String(row.priceUsd)} (got ${String(product.priceUsd)})`);
    }
    if (row.status === "hold" && product.priceUsd !== null) {
      throw new Error(`Mã ${ma} is Hold — no USD`);
    }
  }
}
