import { applyHubColorNames } from "@/lib/hub-import";
import { applyRecordedHubSourceLink, recordedHubSourceLink } from "@/lib/hub-source-links";
import { CATALOG_SCHEMA, KNOWN_SEED_MAS, isKnownSeedMa } from "@/lib/catalog-contract";
import { assertHandoffExportText } from "@/lib/handoff-json";
import { catalogProductsInOrder } from "@/lib/sell-contract";
import { asCatalogDocument, parseCatalogDocument, toCatalogDocumentJson } from "@/lib/product-parse";
import { siteId } from "@/lib/site-runtime";
import type { CatalogDocument, Product, SiteSettings } from "@/lib/types";

function overlayProduct(base: Product | undefined, incoming: Product): Product {
  if (!base) {
    return incoming;
  }
  return {
    ...incoming,
    titleEn: incoming.titleEn.trim() || base.titleEn,
    titleVn: incoming.titleVn.trim() || base.titleVn,
    descriptionEn: incoming.descriptionEn.trim() || base.descriptionEn,
    descriptionVn: incoming.descriptionVn.trim() || base.descriptionVn,
    images: incoming.images.length > 0 ? incoming.images : base.images,
    colors: incoming.colors.length > 0 ? incoming.colors : base.colors,
    sizes: incoming.sizes.length > 0 ? incoming.sizes : base.sizes,
    sourceLink: incoming.sourceLink ?? base.sourceLink ?? recordedHubSourceLink(incoming.ma),
    fulfillment: incoming.fulfillment || base.fulfillment,
  };
}

function rawHasSettings(raw: unknown): boolean {
  return typeof raw === "object" && raw !== null && "settings" in raw && raw.settings != null;
}

/**
 * Overlay kit / official catalog.v1 onto the live shop document.
 * Replace updates matching mãs (and keeps live extras). Merge is the same overlay plus new incoming extras.
 * Empty kit titles do not wipe shop copy. OneDrive photo paths are already dropped in parse.
 */
export function applyCatalogHandoff(
  live: CatalogDocument,
  incoming: CatalogDocument,
  mode: "replace" | "merge",
  settings: SiteSettings,
): CatalogDocument {
  const sanitized = applyHubColorNames(incoming.products);
  const liveByMa = new Map(live.products.map((product) => [product.ma, product]));
  const incomingByMa = new Map(sanitized.map((product) => [product.ma, product]));
  const order: string[] = [];

  if (mode === "merge") {
    for (const product of live.products) {
      if (!order.includes(product.ma)) {
        order.push(product.ma);
      }
    }
    for (const product of sanitized) {
      if (!order.includes(product.ma)) {
        order.push(product.ma);
      }
    }
  } else {
    for (const ma of KNOWN_SEED_MAS) {
      if (incomingByMa.has(ma) || liveByMa.has(ma)) {
        order.push(ma);
      }
    }
    for (const product of sanitized) {
      if (!order.includes(product.ma)) {
        order.push(product.ma);
      }
    }
    for (const product of live.products) {
      if (!order.includes(product.ma) && !isKnownSeedMa(product.ma)) {
        order.push(product.ma);
      }
    }
  }

  const products: Product[] = order.map((ma) => {
    const incomingProduct = incomingByMa.get(ma);
    const liveProduct = liveByMa.get(ma);
    if (incomingProduct) {
      return applyRecordedHubSourceLink(overlayProduct(liveProduct, incomingProduct));
    }
    if (liveProduct) {
      return applyRecordedHubSourceLink(liveProduct);
    }
    throw new Error(`Handoff lost mã ${ma}`);
  });

  return asCatalogDocument(products, settings, siteId());
}

export function settingsForHandoffImport(raw: unknown, live: SiteSettings, parsed: SiteSettings): SiteSettings {
  return rawHasSettings(raw) ? parsed : live;
}

/** Official handoff file: allowlist + hub-first products. No OD source path. */
export function toHandoffCatalogJson(document: CatalogDocument): string {
  const normalized = parseCatalogDocument(document);
  const payload = {
    schema: CATALOG_SCHEMA,
    version: 1 as const,
    siteId: normalized.siteId,
    allowlist: [...KNOWN_SEED_MAS],
    products: catalogProductsInOrder(normalized.products),
    settings: normalized.settings,
    ...(normalized.updatedAt ? { updatedAt: normalized.updatedAt } : {}),
  };
  return `${JSON.stringify(payload, null, 2)}\n`;
}

export function parseHandoffCatalog(raw: unknown): CatalogDocument {
  return parseCatalogDocument(raw);
}

export function assertHandoffJson(json: string): void {
  assertHandoffExportText(json);
  toCatalogDocumentJson(parseCatalogDocument(JSON.parse(json) as unknown));
}

/** Export → parse → replace overlay must keep mãs, prices, Hold, and live extras (A03+). */
export function roundTripHandoffCatalog(live: CatalogDocument): CatalogDocument {
  const json = toHandoffCatalogJson(live);
  assertHandoffJson(json);
  const parsed = parseHandoffCatalog(JSON.parse(json) as unknown);
  const liveMas = [...live.products.map((product) => product.ma)].sort().join(",");
  const parsedMas = [...parsed.products.map((product) => product.ma)].sort().join(",");
  if (liveMas !== parsedMas) {
    throw new Error(`Handoff round-trip mã set changed: ${liveMas} → ${parsedMas}`);
  }
  for (const product of live.products) {
    const next = parsed.products.find((row) => row.ma === product.ma);
    if (!next) {
      throw new Error(`Handoff round-trip lost ${product.ma}`);
    }
    if (next.priceUsd !== product.priceUsd) {
      throw new Error(`Handoff round-trip changed price on ${product.ma}`);
    }
    if (next.status !== product.status) {
      throw new Error(`Handoff round-trip changed status on ${product.ma}`);
    }
    if (next.titleEn !== product.titleEn) {
      throw new Error(`Handoff round-trip changed title on ${product.ma}`);
    }
  }
  const replaced = applyCatalogHandoff(live, parsed, "replace", live.settings);
  for (const extra of live.products.filter((product) => !isKnownSeedMa(product.ma))) {
    const kept = replaced.products.find((row) => row.ma === extra.ma);
    if (!kept || kept.titleEn !== extra.titleEn) {
      throw new Error(`Handoff replace after export lost extra ${extra.ma}`);
    }
  }
  return parsed;
}
