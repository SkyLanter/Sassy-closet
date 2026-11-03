import { KNOWN_SEED_MAS } from "@/lib/catalog-contract";
import type { Product } from "@/lib/types";

/**
 * Hub ten must exist in seed. Available needs a USD price; Hold has none.
 * The dollar is the catalog `priceUsd` (Blob). This check does not freeze a list.
 */
export function assertBossPrices(products: Product[]): void {
  const byMa = new Map(products.map((product) => [product.ma, product]));
  for (const ma of KNOWN_SEED_MAS) {
    const product = byMa.get(ma);
    if (!product) {
      throw new Error(`Missing hub mã ${ma}`);
    }
    switch (product.status) {
      case "hold":
        if (product.priceUsd !== null) {
          throw new Error(`Mã ${ma} is Hold — no USD`);
        }
        break;
      case "available":
        if (product.priceUsd === null) {
          throw new Error(`Mã ${ma} is Available and needs a USD price`);
        }
        break;
      case "sold":
        break;
      default: {
        const _exhaustive: never = product.status;
        throw new Error(`Mã ${ma} has unknown status ${String(_exhaustive)}`);
      }
    }
  }
}
