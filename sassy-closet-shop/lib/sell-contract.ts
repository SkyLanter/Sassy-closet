import { bossRow } from "@/lib/boss-catalog";
import { KNOWN_SEED_MAS, isKnownSeedMa } from "@/lib/catalog-contract";
import { isValidMa, normalizeMa } from "@/lib/ma";
import type { Product, ProductStatus } from "@/lib/types";

const OFFICIAL_MA_RE = /^(AO|QU|VA|AK|GI|PK|SET)\d+$/i;

function isOfficialAlphabetMa(ma: string): boolean {
  return OFFICIAL_MA_RE.test(ma.trim());
}

export const SELL_ALLOWLIST = KNOWN_SEED_MAS;

export const NON_ALLOWLIST_SAVE_ERROR =
  "400: Official/Square alphabet or an invalid letter cannot be saved. Sell-site uses A01, not AO001. Hub mãs stay; next mãs (A03+) Save when Add assigns them.";

export function isSellAllowlistMa(ma: string): boolean {
  return isKnownSeedMa(normalizeMa(ma));
}

export function nonAllowlistSaveError(ma: string): string {
  return `${NON_ALLOWLIST_SAVE_ERROR} (got ${normalizeMa(ma) || ma})`;
}

export function isSellableMa(ma: string): boolean {
  const normalized = normalizeMa(ma);
  return isValidMa(normalized) && !isOfficialAlphabetMa(normalized);
}

/** Hold ⇔ priceUsd null. Available allowlist ⇔ Boss USD. P05 never $23. */
export function assertHoldPricePairing(
  ma: string,
  status: ProductStatus,
  priceUsd: number | null,
): void {
  const normalized = normalizeMa(ma);
  if (normalized === "P05" && priceUsd === 23) {
    throw new Error("P05 must never publish $23.");
  }
  switch (status) {
    case "hold":
      if (priceUsd !== null) {
        throw new Error(`Hold ${normalized} cannot have a USD price (P02/P05 never $23).`);
      }
      return;
    case "available": {
      if (priceUsd === null) {
        throw new Error(`Available ${normalized} needs a USD price.`);
      }
      const row = bossRow(normalized);
      if (row) {
        if (row.priceUsd === null) {
          throw new Error(`${normalized} is Hold-only on the Boss list — cannot Save as Available.`);
        }
        if (priceUsd !== row.priceUsd) {
          throw new Error(`${normalized} Available price must be $${row.priceUsd} (Boss list).`);
        }
      }
      return;
    }
    case "sold":
      return;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

/** Price lock for shop + staff export. Keeps a recorded staff `sourceLink`. */
export function publicSafeProduct(product: Product): Product {
  switch (product.status) {
    case "hold":
      return { ...product, priceUsd: null };
    case "available": {
      const row = bossRow(product.ma);
      if (row && row.priceUsd !== null) {
        return { ...product, priceUsd: row.priceUsd };
      }
      return product;
    }
    case "sold":
      return product;
    default: {
      const _exhaustive: never = product.status;
      return _exhaustive;
    }
  }
}

/** Customer tiles / PDP / JSON-LD — no factory URL. */
export function shopSafeProduct(product: Product): Product {
  return { ...publicSafeProduct(product), sourceLink: null };
}

export function allowlistProductsInOrder(products: Product[]): Product[] {
  const byMa = new Map(products.map((product) => [normalizeMa(product.ma), product]));
  const rows: Product[] = [];
  for (const ma of KNOWN_SEED_MAS) {
    const product = byMa.get(ma);
    if (product) {
      rows.push(publicSafeProduct(product));
    }
  }
  return rows;
}

/** Hub ten first (Boss order), then Boss-added extras (A03+). */
export function catalogProductsInOrder(products: Product[]): Product[] {
  const hub = allowlistProductsInOrder(products);
  const hubSet = new Set(hub.map((product) => normalizeMa(product.ma)));
  const extras = products
    .filter((product) => !hubSet.has(normalizeMa(product.ma)))
    .map(publicSafeProduct);
  return [...hub, ...extras];
}

export function assertImportSellContract(products: Product[]): void {
  const present = new Set(products.map((product) => normalizeMa(product.ma)));
  const missing = KNOWN_SEED_MAS.filter((ma) => !present.has(ma));
  if (missing.length > 0) {
    throw new Error(
      `Import rejected missing hub mãs: ${missing.join(", ")}. Do not invent replacements.`,
    );
  }
  const seen = new Set<string>();
  for (const product of products) {
    const ma = normalizeMa(product.ma);
    if (seen.has(ma)) {
      throw new Error(`Import rejected duplicate mã ${ma}. Do not gộp.`);
    }
    seen.add(ma);
    if (!isSellableMa(ma)) {
      throw new Error(
        isOfficialAlphabetMa(ma)
          ? `Import rejected Official alphabet ${product.ma}. Sell-site uses A01, not AO001.`
          : `Import rejected invalid mã ${product.ma}.`,
      );
    }
    assertHoldPricePairing(product.ma, product.status, product.priceUsd);
  }
}
