import { parseCatalogDocument, toCatalogDocumentJson } from "@/lib/product-parse";
import type { CatalogDocument, Product } from "@/lib/types";

const ROUND_TRIP_DIFF_CAP = 12;

export const BLOB_READBACK_DELAYS_MS = [0, 80, 200, 450, 900] as const;

export async function waitMs(ms: number): Promise<void> {
  if (ms <= 0) {
    return;
  }
  await new Promise<void>((resolve) => {
    setTimeout(resolve, ms);
  });
}

export function canonicalCatalogJson(value: unknown): string {
  return toCatalogDocumentJson(parseCatalogDocument(value));
}

export function catalogJsonMatches(expectedJson: string, raw: unknown): boolean {
  try {
    return canonicalCatalogJson(raw) === expectedJson;
  } catch {
    return false;
  }
}

function withFixedClock(document: CatalogDocument): CatalogDocument {
  return { ...document, updatedAt: "1970-01-01T00:00:00.000Z" };
}

/** Same catalog.v1 body as the put — ignores a stale Blob `updatedAt`. */
export function catalogBodyMatches(expectedJson: string, raw: unknown): boolean {
  try {
    const expected = withFixedClock(parseCatalogDocument(JSON.parse(expectedJson) as unknown));
    const actual = withFixedClock(parseCatalogDocument(raw));
    return toCatalogDocumentJson(expected) === toCatalogDocumentJson(actual);
  } catch {
    return false;
  }
}

function preview(value: unknown): string {
  if (value === undefined) {
    return "∅";
  }
  if (typeof value === "string") {
    return JSON.stringify(value.length > 64 ? `${value.slice(0, 61)}…` : value);
  }
  try {
    const json = JSON.stringify(value);
    return json.length > 80 ? `${json.slice(0, 77)}…` : json;
  } catch {
    return String(value);
  }
}

function pushDiff(diffs: string[], path: string, expected: unknown, actual: unknown): void {
  if (JSON.stringify(expected) === JSON.stringify(actual)) {
    return;
  }
  diffs.push(`${path}: ${preview(expected)} → ${preview(actual)}`);
}

function productDiffs(ma: string, expected: Product, actual: Product | undefined): string[] {
  if (!actual) {
    return [`products[${ma}]: missing on read-back`];
  }
  const diffs: string[] = [];
  const keys: Array<keyof Product> = [
    "type",
    "titleEn",
    "titleVn",
    "status",
    "priceUsd",
    "qty",
    "descriptionEn",
    "descriptionVn",
    "fulfillment",
    "sourceLink",
  ];
  for (const key of keys) {
    pushDiff(diffs, `products[${ma}].${key}`, expected[key], actual[key]);
  }
  pushDiff(diffs, `products[${ma}].sizes`, expected.sizes, actual.sizes);
  pushDiff(diffs, `products[${ma}].fitCm`, expected.fitCm, actual.fitCm);
  pushDiff(diffs, `products[${ma}].colors`, expected.colors, actual.colors);
  pushDiff(diffs, `products[${ma}].images`, expected.images, actual.images);
  return diffs;
}

export function catalogFieldDiffs(expected: CatalogDocument, actual: CatalogDocument): string[] {
  const diffs: string[] = [];
  pushDiff(diffs, "schema", expected.schema, actual.schema);
  pushDiff(diffs, "version", expected.version, actual.version);
  pushDiff(diffs, "siteId", expected.siteId, actual.siteId);
  pushDiff(diffs, "updatedAt", expected.updatedAt ?? null, actual.updatedAt ?? null);
  pushDiff(
    diffs,
    "settings.announcementLines",
    expected.settings.announcementLines,
    actual.settings.announcementLines,
  );
  pushDiff(
    diffs,
    "settings.facebookPageUrl",
    expected.settings.facebookPageUrl,
    actual.settings.facebookPageUrl,
  );

  const expectedMas = expected.products.map((product) => product.ma);
  const actualMas = actual.products.map((product) => product.ma);
  if (expectedMas.join(" ") !== actualMas.join(" ")) {
    diffs.push(`products order: ${expectedMas.join(",")} → ${actualMas.join(",")}`);
  }

  const actualByMa = new Map(actual.products.map((product) => [product.ma, product]));
  for (const product of expected.products) {
    diffs.push(...productDiffs(product.ma, product, actualByMa.get(product.ma)));
  }
  for (const product of actual.products) {
    if (!expected.products.some((row) => row.ma === product.ma)) {
      diffs.push(`products[${product.ma}]: extra on read-back`);
    }
  }
  return diffs.slice(0, ROUND_TRIP_DIFF_CAP);
}

export function roundTripMismatchError(expectedJson: string, raw: unknown): string {
  const prefix = "Blob write did not round-trip: read-back JSON does not match what was saved.";
  if (raw === null || raw === undefined) {
    return `${prefix} Read-back was empty.`;
  }
  try {
    const expected = parseCatalogDocument(JSON.parse(expectedJson) as unknown);
    const actual = parseCatalogDocument(raw);
    const diffs = catalogFieldDiffs(expected, actual);
    if (diffs.length === 0) {
      return `${prefix} Canonical parse matched but serialized JSON did not (key order or whitespace).`;
    }
    return `${prefix} ${diffs.join("; ")}`;
  } catch (error) {
    const detail = error instanceof Error ? error.message : "invalid catalog.v1";
    return `${prefix} Read-back did not parse (${detail}).`;
  }
}
