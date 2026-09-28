import { bossRow, warnBossPriceLag } from "@/lib/boss-catalog";
import { KNOWN_SEED_MAS, isKnownSeedMa } from "@/lib/catalog-contract";
import { isValidMa, normalizeMa } from "@/lib/ma";
import type { CatalogDocument, Product, ProductStatus } from "@/lib/types";

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

/** Hold ⇔ priceUsd null. Available allowlist ⇔ Boss USD. */
export function assertHoldPricePairing(
  ma: string,
  status: ProductStatus,
  priceUsd: number | null,
): void {
  const normalized = normalizeMa(ma);
  switch (status) {
    case "hold":
      if (priceUsd !== null) {
        throw new Error(`Hold ${normalized} cannot have a USD price.`);
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
        if (product.priceUsd !== row.priceUsd) {
          warnBossPriceLag(product.ma, product.priceUsd, row.priceUsd);
        }
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

/**
 * Live catalog reads show Boss USD for locked mãs.
 * Stored Blob can still have the 2026-09-27 price until the merge-time catalog patch.
 * A lagging price logs a warning and the lock wins. Admin saves still reject a non-lock USD.
 * Writes do not call this — a raw document with any other locked price is still rejected.
 */
export function presentLockedBossPrices(document: CatalogDocument): CatalogDocument {
  return {
    ...document,
    products: document.products.map(publicSafeProduct),
  };
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
