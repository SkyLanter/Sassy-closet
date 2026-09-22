import { KNOWN_SEED_MAS, type KnownSeedMa } from "@/lib/catalog-contract";
import type { Product, ProductStatus } from "@/lib/types";

export type BossPriceRow = {
  ma: KnownSeedMa;
  priceUsd: number | null;
  status: ProductStatus;
};

/** Boss-locked sell prices. Do not invent mãs or USD. Hold has no price. */
export const BOSS_PRICE_LIST: readonly BossPriceRow[] = [
  { ma: "A01", priceUsd: 30, status: "available" },
  { ma: "S01", priceUsd: 45, status: "available" },
  { ma: "P01", priceUsd: 8, status: "available" },
  { ma: "P02", priceUsd: 28, status: "available" },
  { ma: "P03", priceUsd: 15, status: "available" },
  { ma: "P04", priceUsd: 12, status: "available" },
  { ma: "P05", priceUsd: 28, status: "available" },
  { ma: "K01", priceUsd: 40, status: "available" },
  { ma: "H01", priceUsd: 10, status: "available" },
  { ma: "A02", priceUsd: 26, status: "available" },
] as const;

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
