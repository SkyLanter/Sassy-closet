import { isSiteId, siteId } from "@/lib/site-runtime";

/** Portable catalog identity. Official and test shops speak this file. */
export const CATALOG_SCHEMA = "catalog.v1" as const;
export const CATALOG_VERSION = 1 as const;

export const KNOWN_SEED_MAS = [
  "A01",
  "S01",
  "P01",
  "P02",
  "P03",
  "P04",
  "P05",
  "K01",
  "H01",
  "A02",
] as const;

export type KnownSeedMa = (typeof KNOWN_SEED_MAS)[number];

export function catalogBlobPrefix(id = siteId()): string {
  return `${id}/`;
}

export function catalogBlobPath(id = siteId()): string {
  return `${id}/catalog.v1.json`;
}

/** Older Blob keys this test shop used before catalog.v1. Read-only fallback. */
export function catalogBlobLegacyPaths(id = siteId()): string[] {
  const paths = [`${id}/catalog.json`];
  if (id !== "sassy-closet-shop") {
    paths.push("sassy-closet-shop/catalog.json");
  }
  return paths;
}

export function catalogBlobProbePath(id = siteId()): string {
  return `${id}/persist-probe.json`;
}

export function catalogKvKey(id = siteId()): string {
  return `${id}:catalog.v1`;
}

export function catalogImagePrefix(ma: string, id = siteId()): string {
  return `${id}/products/${ma}`;
}

export function catalogExportFilename(id = siteId()): string {
  return `${id}-catalog.v1.json`;
}

export function normalizeCatalogSiteId(value: unknown, fallback = siteId()): string {
  if (typeof value === "string" && isSiteId(value)) {
    return value.trim().toLowerCase();
  }
  return fallback;
}

export function isCatalogSchema(value: unknown): value is typeof CATALOG_SCHEMA {
  return value === CATALOG_SCHEMA;
}

export function isKnownSeedMa(ma: string): ma is KnownSeedMa {
  return (KNOWN_SEED_MAS as readonly string[]).includes(ma);
}
