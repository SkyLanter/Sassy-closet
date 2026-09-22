import { KNOWN_SEED_MAS, isKnownSeedMa } from "@/lib/catalog-contract";
import { normalizeMa } from "@/lib/ma";
import { assertHoldPricePairing } from "@/lib/sell-contract";
import type { Product } from "@/lib/types";

const OFFICIAL_MA_RE = /^(AO|QU|VA|AK|GI|PK|SET)\d+$/i;

export class CatalogCorruptError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CatalogCorruptError";
  }
}

export function isCatalogCorruptError(error: unknown): boolean {
  return error instanceof CatalogCorruptError || (error instanceof Error && error.name === "CatalogCorruptError");
}

export function looksLikeOfficialMa(ma: string): boolean {
  return OFFICIAL_MA_RE.test(ma.trim());
}

export type CatalogIntegrity = {
  missingAllowlist: string[];
  extras: string[];
  duplicates: string[];
  officialAlphabet: string[];
  soldHidden: string[];
};

export function inspectCatalogIntegrity(products: Product[]): CatalogIntegrity {
  const seen = new Map<string, number>();
  const extras: string[] = [];
  const officialAlphabet: string[] = [];
  const soldHidden: string[] = [];
  for (const product of products) {
    const ma = normalizeMa(product.ma);
    seen.set(ma, (seen.get(ma) ?? 0) + 1);
    if (!isKnownSeedMa(ma)) {
      extras.push(product.ma);
    }
    if (looksLikeOfficialMa(product.ma)) {
      officialAlphabet.push(product.ma);
    }
    if (product.status === "sold") {
      soldHidden.push(product.ma);
    }
  }
  const duplicates = [...seen.entries()].filter(([, count]) => count > 1).map(([ma]) => ma);
  const present = new Set(products.map((product) => normalizeMa(product.ma)));
  const missingAllowlist = KNOWN_SEED_MAS.filter((ma) => !present.has(ma));
  return { missingAllowlist, extras, duplicates, officialAlphabet, soldHidden };
}

export function assertUniqueNormalizedMas(products: Product[]): void {
  const seen = new Set<string>();
  for (const product of products) {
    const ma = normalizeMa(product.ma);
    if (seen.has(ma)) {
      throw new Error(`Duplicate mã ${ma}. Do not gộp two pieces. Pick a Boss-assigned code.`);
    }
    seen.add(ma);
  }
}

export function assertAllowlistPresent(products: Product[]): void {
  const present = new Set(products.map((product) => normalizeMa(product.ma)));
  const missing = KNOWN_SEED_MAS.filter((ma) => !present.has(ma));
  if (missing.length > 0) {
    throw new Error(
      `Catalog is missing allowlist mãs: ${missing.join(", ")}. Do not invent replacements. Restore from seed or a good export.`,
    );
  }
}

export function assertNoOfficialAlphabet(products: Product[]): void {
  const bad = products.filter((product) => looksLikeOfficialMa(product.ma));
  if (bad.length > 0) {
    throw new Error(
      `Official/Square alphabet on sell catalog: ${bad.map((product) => product.ma).join(", ")}. Sell-site uses A01, not AO001.`,
    );
  }
}

/** Live document: all ten must exist, unique, no Official alphabet. Leftover extras may remain until Remove. */
export function assertLiveCatalogIntegrity(products: Product[]): void {
  assertUniqueNormalizedMas(products);
  assertAllowlistPresent(products);
  assertNoOfficialAlphabet(products);
  for (const product of products) {
    if (isKnownSeedMa(normalizeMa(product.ma))) {
      assertHoldPricePairing(product.ma, product.status, product.priceUsd);
    }
  }
}

export function assertWrittenProductFacts(products: Product[], expected: Product): void {
  const row = products.find((product) => product.ma === expected.ma);
  if (!row) {
    throw new Error(
      `Save did not read back ${expected.ma}. The shop may still show seed or an old list.`,
    );
  }
  if (row.titleEn !== expected.titleEn) {
    throw new Error(`Save did not persist the title for ${expected.ma}.`);
  }
  if (row.status !== expected.status) {
    throw new Error(`Save did not persist status for ${expected.ma}.`);
  }
  if (row.priceUsd !== expected.priceUsd) {
    throw new Error(`Save did not persist price for ${expected.ma}.`);
  }
}
