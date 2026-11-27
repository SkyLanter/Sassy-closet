import { KNOWN_SEED_MAS, isKnownSeedMa } from "@/lib/catalog-contract";
import { canonicalMaSpelling, isCanonicalMaSpelling, isValidMa, normalizeMa } from "@/lib/ma";
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

/** Largest catalog USD the intake shop-tools desk reads back. Above it, the desk rejects the whole file. */
export const MAX_CATALOG_PRICE_USD = 100000;

/**
 * The one USD shape both apps accept: 0–100000, a finite number, and whole cents.
 * `sassy-closet/lib/shop-catalog.ts` readPrice is the desk side of this contract;
 * a price that fails here is a price the desk cannot list or re-save.
 */
export function catalogPriceError(ma: string, priceUsd: number): string | null {
  if (!Number.isFinite(priceUsd) || priceUsd < 0 || priceUsd > MAX_CATALOG_PRICE_USD) {
    return `Mã ${ma} has an invalid USD price. The intake desk reads $0–$${MAX_CATALOG_PRICE_USD}.`;
  }
  const cents = Math.round(priceUsd * 100);
  if (Math.abs(priceUsd * 100 - cents) > 1e-6) {
    return `Mã ${ma} price must be dollars and cents. The intake desk rejects a fraction of a cent.`;
  }
  return null;
}

/**
 * S06 stays $25 under S06 / S6 / s006. A blank price is not a second dollar.
 * Padded spellings are still rejected by the import gate before this runs.
 */
export function s06PriceLockError(ma: string, priceUsd: number | null): string | null {
  if (canonicalMaSpelling(ma) !== "S06") {
    return null;
  }
  if (priceUsd !== null && priceUsd !== 25) {
    return "Import rejected S06 price. S06 stays $25.";
  }
  return null;
}

/** Hold ⇔ priceUsd null. Available needs the catalog USD. Sold may keep a price. */
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
    case "available":
      if (priceUsd === null) {
        throw new Error(`Available ${normalized} needs a USD price.`);
      }
      return;
    case "sold":
      return;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

/** Shop + staff export. Hold clears USD. Available and sold keep catalog priceUsd. */
export function publicSafeProduct(product: Product): Product {
  switch (product.status) {
    case "hold":
      return { ...product, priceUsd: null };
    case "available":
    case "sold":
      return product;
    default: {
      const _exhaustive: never = product.status;
      return _exhaustive;
    }
  }
}

/**
 * Live catalog reads publish stored priceUsd.
 * Hold is forced to null. Available dollars stay whatever Blob (or seed) stored.
 * Writes do not call this.
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
    if (seen.has(canonicalMaSpelling(ma))) {
      throw new Error(`Import rejected duplicate mã ${canonicalMaSpelling(ma)}. Do not gộp.`);
    }
    seen.add(canonicalMaSpelling(ma));
    if (!isCanonicalMaSpelling(ma)) {
      throw new Error(`Import rejected padded mã ${product.ma}. Use ${canonicalMaSpelling(ma)}.`);
    }
    if (!isSellableMa(ma)) {
      throw new Error(
        isOfficialAlphabetMa(ma)
          ? `Import rejected Official alphabet ${product.ma}. Sell-site uses A01, not AO001.`
          : `Import rejected invalid mã ${product.ma}.`,
      );
    }
    assertHoldPricePairing(product.ma, product.status, product.priceUsd);
    const locked = s06PriceLockError(ma, product.priceUsd);
    if (locked) {
      throw new Error(locked);
    }
    if (product.priceUsd !== null) {
      // Shop-tools desk reads this same file; a sub-cent or out-of-range USD wedges every save there.
      const unreadable = catalogPriceError(ma, product.priceUsd);
      if (unreadable) {
        throw new Error(`Import rejected ${unreadable}`);
      }
    }
  }
}
