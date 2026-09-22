import { parseAsiaSizes, parseFitCm } from "@/lib/asia-size";
import { looksLikeOfficialMa } from "@/lib/catalog-integrity";
import { CATALOG_SCHEMA, normalizeCatalogSiteId } from "@/lib/catalog-contract";
import { isColorId, parseProductColor } from "@/lib/colors";
import { sortImagesByOrder } from "@/lib/hub-colors";
import { parseFulfillment } from "@/lib/fulfillment";
import { assertKitAllowlist, isBlobDraftSrc, isHqDiskPhotoPath, sellTypeAccepted } from "@/lib/kit-catalog";
import { isValidMa, maLetter, normalizeMa } from "@/lib/ma";
import { parseSiteSettings } from "@/lib/site-settings";
import { siteId } from "@/lib/site-runtime";
import { parseSourceLink } from "@/lib/source-link";
import type {
  CatalogDocument,
  Product,
  ProductColor,
  ProductImageAsset,
  ProductStatus,
  SiteSettings,
} from "@/lib/types";

function isStatus(value: string): value is ProductStatus {
  return value === "available" || value === "hold" || value === "sold";
}

export function isAllowedImageSrc(src: string): boolean {
  const trimmed = src.trim();
  if (trimmed.startsWith("/") && !trimmed.startsWith("//")) {
    return true;
  }
  try {
    const url = new URL(trimmed);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
}

function parseColors(raw: unknown, ma: string): ProductColor[] {
  if (raw === undefined) {
    return [];
  }
  if (!Array.isArray(raw)) {
    throw new Error(`Mã ${ma} colors must be an array`);
  }
  const colors = raw.map((item, index) => parseProductColor(item, ma, index));
  const seen = new Set<string>();
  for (const color of colors) {
    if (seen.has(color.id)) {
      throw new Error(`Mã ${ma} has a duplicate color id`);
    }
    seen.add(color.id);
  }
  return colors;
}

function parseImageAsset(
  raw: unknown,
  ma: string,
  index: number,
  colorIds: Set<string>,
): ProductImageAsset | null {
  if (typeof raw === "string") {
    const src = raw.trim();
    if (!src) {
      return null;
    }
    if (!isAllowedImageSrc(src)) {
      throw new Error(`Mã ${ma} has an invalid image URL`);
    }
    return { src, colorId: null, order: index + 1 };
  }
  if (typeof raw !== "object" || raw === null) {
    throw new Error(`Mã ${ma} image ${index} is invalid`);
  }
  const row = raw as Record<string, unknown>;
  const srcRaw = typeof row.src === "string" ? row.src : typeof row.url === "string" ? row.url : "";
  if (typeof srcRaw !== "string") {
    throw new Error(`Mã ${ma} image ${index} needs src`);
  }
  const src = srcRaw.trim();
  if (!src) {
    return null;
  }
  if (isHqDiskPhotoPath(src) || isBlobDraftSrc(src)) {
    return null;
  }
  if (!isAllowedImageSrc(src)) {
    throw new Error(`Mã ${ma} has an invalid image URL`);
  }
  const colorRaw = row.colorId;
  const trimmedId = typeof colorRaw === "string" ? colorRaw.trim() : "";
  const colorId =
    trimmedId && isColorId(trimmedId) && colorIds.has(trimmedId) ? trimmedId : null;
  const orderRaw = row.order;
  const order =
    typeof orderRaw === "number" && Number.isFinite(orderRaw) && orderRaw > 0
      ? Math.floor(orderRaw)
      : index + 1;
  return { src, colorId, order };
}

function priceForStatus(status: ProductStatus, priceUsd: number | null, ma: string): number | null {
  switch (status) {
    case "available":
      if (priceUsd === null) {
        throw new Error(`Mã ${ma} is available but missing USD price`);
      }
      return priceUsd;
    case "hold":
      return null;
    case "sold":
      return priceUsd;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

export function parseProduct(raw: unknown, index: number): Product {
  if (typeof raw !== "object" || raw === null) {
    throw new Error(`Product ${index} is not an object`);
  }

  const row = raw as Record<string, unknown>;
  const maValue = row.ma;
  if (typeof maValue === "string" && looksLikeOfficialMa(maValue)) {
    throw new Error(
      `Mã ${maValue.trim().toUpperCase()} is Official/Square alphabet. Sell-site uses A01, not AO001. Never invent a bridge.`,
    );
  }
  if (typeof maValue !== "string" || !isValidMa(maValue)) {
    throw new Error(`Invalid mã at catalog index ${index}`);
  }

  const ma = normalizeMa(maValue);
  const type = maLetter(ma);
  if (type === null) {
    throw new Error(`Mã ${ma} has no type letter`);
  }
  if (!sellTypeAccepted(type, row.type)) {
    throw new Error(`Mã ${ma} type mismatch (expected ${type})`);
  }

  const status = row.status;
  if (typeof status !== "string" || !isStatus(status)) {
    throw new Error(`Mã ${ma} has invalid status`);
  }

  const qty = row.qty;
  if (qty !== 1) {
    throw new Error(`Mã ${ma} qty must be 1`);
  }

  const priceUsd = row.priceUsd;
  if (priceUsd !== null && (typeof priceUsd !== "number" || !Number.isFinite(priceUsd))) {
    throw new Error(`Mã ${ma} has invalid priceUsd`);
  }

  const colors = parseColors(row.colors, ma);
  const colorIds = new Set(colors.map((color) => color.id));

  const images = row.images;
  if (!Array.isArray(images)) {
    throw new Error(`Mã ${ma} images must be an array`);
  }
  const imageList: ProductImageAsset[] = [];
  for (const [imageIndex, item] of images.entries()) {
    const parsed = parseImageAsset(item, ma, imageIndex, colorIds);
    if (parsed) {
      imageList.push(parsed);
    }
  }
  imageList.splice(0, imageList.length, ...sortImagesByOrder(imageList));

  const titleVn = typeof row.titleVn === "string" ? row.titleVn : "";
  const titleEn = typeof row.titleEn === "string" ? row.titleEn : "";
  const descriptionVn = typeof row.descriptionVn === "string" ? row.descriptionVn : "";
  const descriptionEn = typeof row.descriptionEn === "string" ? row.descriptionEn : "";

  return {
    ma,
    type,
    titleVn: titleVn.trim(),
    titleEn: titleEn.trim(),
    priceUsd: priceForStatus(status, priceUsd, ma),
    qty: 1,
    status,
    colors,
    images: imageList,
    sizes: parseAsiaSizes(row.sizes),
    fitCm: parseFitCm(row.fitCm),
    descriptionVn: descriptionVn.trim(),
    descriptionEn: descriptionEn.trim(),
    fulfillment: parseFulfillment(row.fulfillment, ma),
    sourceLink: parseSourceLink(row.sourceLink ?? row.source_link, ma),
  };
}

export function parseCatalog(raw: unknown): Product[] {
  if (!Array.isArray(raw)) {
    throw new Error("Catalog must be an array");
  }
  const products = raw.map((row, index) => parseProduct(row, index));
  const seen = new Set<string>();
  for (const product of products) {
    if (seen.has(product.ma)) {
      throw new Error(`Duplicate mã ${product.ma}`);
    }
    seen.add(product.ma);
  }
  if (products.length === 0) {
    throw new Error("Catalog cannot be empty");
  }
  return products;
}

function parseUpdatedAt(value: unknown): string | undefined {
  if (typeof value !== "string" || !value.trim()) {
    return undefined;
  }
  const ms = Date.parse(value);
  if (!Number.isFinite(ms)) {
    return undefined;
  }
  return new Date(ms).toISOString();
}

export function asCatalogDocument(
  products: Product[],
  settings: SiteSettings,
  id = siteId(),
  updatedAt?: string,
): CatalogDocument {
  const document: CatalogDocument = {
    schema: CATALOG_SCHEMA,
    version: 1,
    siteId: normalizeCatalogSiteId(id),
    products,
    settings,
  };
  const stamped = parseUpdatedAt(updatedAt);
  if (stamped) {
    document.updatedAt = stamped;
  }
  return document;
}

export function stampCatalogUpdatedAt(document: CatalogDocument, at = new Date()): CatalogDocument {
  return asCatalogDocument(document.products, document.settings, document.siteId, at.toISOString());
}

export function parseCatalogDocument(raw: unknown): CatalogDocument {
  if (Array.isArray(raw)) {
    return asCatalogDocument(parseCatalog(raw), parseSiteSettings(null));
  }
  if (typeof raw !== "object" || raw === null) {
    throw new Error("Catalog document is invalid");
  }
  const row = raw as Record<string, unknown>;
  if (row.schema !== undefined && row.schema !== CATALOG_SCHEMA) {
    throw new Error(`Unsupported catalog schema ${String(row.schema)}`);
  }
  if (row.version !== undefined && row.version !== 1) {
    throw new Error(`Unsupported catalog version ${String(row.version)}`);
  }
  if (!Array.isArray(row.products)) {
    throw new Error("Catalog document needs a products array");
  }
  assertKitAllowlist(row.allowlist);
  return asCatalogDocument(
    parseCatalog(row.products),
    parseSiteSettings(row.settings),
    normalizeCatalogSiteId(row.siteId),
    parseUpdatedAt(row.updatedAt),
  );
}

export function toCatalogDocumentJson(document: CatalogDocument): string {
  const normalized = parseCatalogDocument(document);
  return `${JSON.stringify(normalized, null, 2)}\n`;
}

export function assertCanonicalSerializedCatalog(json: string): void {
  const raw: unknown = JSON.parse(json);
  if (typeof raw !== "object" || raw === null || Array.isArray(raw)) {
    throw new Error("Canonical catalog must be a versioned document, not a bare array");
  }
  const row = raw as Record<string, unknown>;
  if (row.schema !== CATALOG_SCHEMA) {
    throw new Error(`Canonical catalog must set schema: ${CATALOG_SCHEMA}`);
  }
  if (row.version !== 1) {
    throw new Error("Canonical catalog must set version: 1");
  }
  if (typeof row.siteId !== "string" || !row.siteId.trim()) {
    throw new Error("Canonical catalog must set siteId");
  }
  if (!Array.isArray(row.products)) {
    throw new Error("Canonical catalog needs a products array");
  }
  if (typeof row.settings !== "object" || row.settings === null) {
    throw new Error("Canonical catalog needs settings");
  }
  if (row.updatedAt !== undefined && (typeof row.updatedAt !== "string" || !Number.isFinite(Date.parse(row.updatedAt)))) {
    throw new Error("Canonical catalog updatedAt must be an ISO timestamp");
  }
  for (const item of row.products) {
    if (typeof item !== "object" || item === null) {
      throw new Error("Canonical product must be an object");
    }
    const product = item as Record<string, unknown>;
    if (!Array.isArray(product.colors)) {
      throw new Error(`Mã ${String(product.ma)} needs a colors array`);
    }
    for (const color of product.colors) {
      if (typeof color !== "object" || color === null) {
        throw new Error(`Mã ${String(product.ma)} has a color that is not an object`);
      }
      const rowColor = color as Record<string, unknown>;
      if (typeof rowColor.id !== "string" || typeof rowColor.hex !== "string" || typeof rowColor.name !== "string") {
        throw new Error(`Mã ${String(product.ma)} color needs id, hex, and name`);
      }
    }
    if (!Array.isArray(product.images)) {
      throw new Error(`Mã ${String(product.ma)} needs an images array`);
    }
    for (const image of product.images) {
      if (typeof image === "string") {
        throw new Error(`Mã ${String(product.ma)} still has a legacy string image`);
      }
      if (typeof image !== "object" || image === null) {
        throw new Error(`Mã ${String(product.ma)} image must be { src, colorId, order }`);
      }
      const rowImage = image as Record<string, unknown>;
      if (typeof rowImage.src !== "string") {
        throw new Error(`Mã ${String(product.ma)} image needs src`);
      }
      if (!("colorId" in rowImage)) {
        throw new Error(`Mã ${String(product.ma)} image needs colorId (string or null)`);
      }
      if (rowImage.colorId !== null && typeof rowImage.colorId !== "string") {
        throw new Error(`Mã ${String(product.ma)} image colorId must be string or null`);
      }
      if (typeof rowImage.order !== "number" || !Number.isFinite(rowImage.order) || rowImage.order < 1) {
        throw new Error(`Mã ${String(product.ma)} image needs a positive order`);
      }
    }
    if (product.fulfillment !== "dropship" && product.fulfillment !== "on_hand") {
      throw new Error(`Mã ${String(product.ma)} needs fulfillment dropship or on_hand`);
    }
    if (product.sourceLink !== null && typeof product.sourceLink !== "string") {
      throw new Error(`Mã ${String(product.ma)} sourceLink must be a string or null`);
    }
    if (product.sizes !== undefined && !Array.isArray(product.sizes)) {
      throw new Error(`Mã ${String(product.ma)} sizes must be an array`);
    }
    if (product.fitCm !== undefined && (typeof product.fitCm !== "object" || product.fitCm === null)) {
      throw new Error(`Mã ${String(product.ma)} fitCm must be an object`);
    }
  }
  parseCatalogDocument(raw);
}

export function assertColorsReadyForSell(product: Product): void {
  const ids = new Set(product.colors.map((color) => color.id));
  for (const color of product.colors) {
    if (!color.name.trim()) {
      throw new Error(`Mã ${product.ma}: each color needs a name for the shop picker`);
    }
    if (!isColorId(color.id)) {
      throw new Error(`Mã ${product.ma}: color id ${color.id} is not a hub slug or generated id`);
    }
  }
  for (const image of product.images) {
    if (image.colorId !== null && !ids.has(image.colorId)) {
      throw new Error(`Mã ${product.ma}: colorId must be null or a color already on this mã`);
    }
  }
}
