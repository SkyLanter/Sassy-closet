import { assertAsiaSizesOnly, assertStoredFitCm, emptyFitCm, type FitCm } from "@/lib/asia-size";
import { mergeColorAssets } from "@/lib/catalog-merge";
import type { Fulfillment } from "@/lib/fulfillment";
import {
  MA_LETTERS,
  isValidMa,
  maLetter,
  nextMaForLetter,
  normalizeMa,
  canonicalMaSpelling,
  isCanonicalMaSpelling,
  type MaLetter,
} from "@/lib/ma";
import { applyRecordedHubColors, bindColorId, stampImageOrders } from "@/lib/hub-colors";
import { srcBelongsToMa } from "@/lib/product-media";
import { assertColorsReadyForSell, isAllowedImageSrc, parseProduct } from "@/lib/product-parse";
import { assertUniqueNormalizedMas, looksLikeOfficialMa } from "@/lib/catalog-integrity";
import { assertHoldPricePairing, isSellableMa, nonAllowlistSaveError } from "@/lib/sell-contract";
import { isKnownSeedMa } from "@/lib/catalog-contract";
import { isOffLiveSell } from "@/lib/held-incomplete";
import { warehouseVoiceError } from "@/lib/warehouse-voice";
import type {
  AsiaSizeLetter,
  Product,
  ProductColor,
  ProductImageAsset,
  ProductStatus,
  ShopSize,
} from "@/lib/types";

export type ProductFieldsInput = {
  titleEn: string;
  titleVn: string;
  descriptionEn: string;
  descriptionVn: string;
  status: string;
  priceUsd: number | null;
  colors: ProductColor[];
  images: ProductImageAsset[];
  sizes?: ShopSize[];
  fitCm?: FitCm;
  fulfillment?: Fulfillment;
  sourceLink?: string | null;
};

export type CatalogMutation =
  | { ok: true; products: Product[]; ma: string }
  | { ok: false; error: string };

function isMaLetter(value: string): value is MaLetter {
  return (MA_LETTERS as readonly string[]).includes(value);
}

/** Catalog row for a mã under any spelling: exact first, then the shared canonical spelling. */
function catalogIndex(catalog: Product[], ma: string): number {
  const exact = catalog.findIndex((product) => product.ma === ma);
  if (exact >= 0) return exact;
  const key = canonicalMaSpelling(ma);
  return key ? catalog.findIndex((product) => canonicalMaSpelling(product.ma) === key) : -1;
}

function maTaken(catalog: Product[], ma: string): boolean {
  const key = canonicalMaSpelling(ma);
  return catalog.some((product) => canonicalMaSpelling(product.ma) === key);
}

function isStatus(value: string): value is ProductStatus {
  return value === "available" || value === "hold" || value === "sold";
}

export function fieldsFromProduct(product: Product): ProductFieldsInput {
  return {
    titleEn: product.titleEn,
    titleVn: product.titleVn,
    descriptionEn: product.descriptionEn,
    descriptionVn: product.descriptionVn,
    status: product.status,
    priceUsd: product.priceUsd,
    colors: product.colors,
    images: product.images,
    sizes: product.sizes,
    fitCm: product.fitCm,
    fulfillment: product.fulfillment,
    sourceLink: product.sourceLink,
  };
}

export function productFromFields(ma: string, input: ProductFieldsInput): Product {
  const type = maLetter(ma);
  if (type === null) {
    throw new Error(`Invalid mã ${ma}`);
  }
  if (!isSellableMa(ma)) {
    throw new Error(nonAllowlistSaveError(ma));
  }
  if (!input.titleEn.trim()) {
    throw new Error("English title is required.");
  }
  if (!isStatus(input.status)) {
    throw new Error("Status must be Hold, Available, or Sold / Gone");
  }
  const status: ProductStatus = input.status;
  let priceUsd: number | null;
  switch (status) {
    case "hold":
      priceUsd = null;
      break;
    case "available":
    case "sold":
      priceUsd = input.priceUsd;
      break;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
  assertHoldPricePairing(ma, status, input.priceUsd);
  assertHoldPricePairing(ma, status, priceUsd);
  const voiceError = warehouseVoiceError(
    input.descriptionEn,
    input.descriptionVn,
    input.fulfillment ?? "dropship",
  );
  if (voiceError) {
    throw new Error(voiceError);
  }
  const sizes = input.sizes ?? [];
  const fitCm = input.fitCm ?? emptyFitCm();
  assertAsiaSizesOnly(sizes);
  assertStoredFitCm(fitCm);
  const product = parseProduct(
    {
      ma,
      type,
      titleEn: input.titleEn,
      titleVn: input.titleVn,
      descriptionEn: input.descriptionEn,
      descriptionVn: input.descriptionVn,
      status,
      priceUsd,
      qty: 1,
      colors: input.colors,
      images: stampImageOrders(
        input.images
          .filter((image) => isAllowedImageSrc(image.src) && srcBelongsToMa(image.src, ma))
          .map((image) => ({
            src: image.src.trim(),
            colorId: bindColorId(input.colors, image.colorId),
            order: image.order,
          })),
      ),
      sizes,
      fitCm,
      fulfillment: input.fulfillment,
      sourceLink: input.sourceLink ?? null,
    },
    0,
  );
  assertColorsReadyForSell(product);
  return applyRecordedHubColors(product);
}

export function addProductToCatalog(
  catalog: Product[],
  letter: string,
  input: ProductFieldsInput,
): CatalogMutation {
  if (!isMaLetter(letter)) {
    return { ok: false, error: "Pick a valid letter (A/Q/V/K/G/P/S/O/H/J/B/D)." };
  }
  const ma = nextMaForLetter(
    letter,
    catalog.map((product) => product.ma),
  );
  if (isOffLiveSell(ma)) {
    return { ok: false, error: `Cannot mint ${ma}.` };
  }
  if (!isSellableMa(ma) || looksLikeOfficialMa(ma)) {
    return { ok: false, error: nonAllowlistSaveError(ma) };
  }
  if (maTaken(catalog, ma)) {
    return { ok: false, error: `Mã ${ma} already exists. Do not gộp. Pick an unused mã.` };
  }
  try {
    const created = productFromFields(ma, input);
    const updated = [...catalog, created];
    assertUniqueNormalizedMas(updated);
    return { ok: true, products: updated, ma };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Add failed" };
  }
}

export function saveProductInCatalog(
  catalog: Product[],
  maInput: string,
  input: ProductFieldsInput,
): CatalogMutation {
  const asked = normalizeMa(maInput);
  if (!isSellableMa(asked)) {
    return { ok: false, error: nonAllowlistSaveError(asked) };
  }
  const index = catalogIndex(catalog, asked);
  if (index < 0) {
    return { ok: false, error: `Mã ${asked} is not in the catalog` };
  }
  // Keep the stored spelling; lock on the canonical one so "S006" / "S6" cannot dodge S06 $25.
  const ma = catalog[index].ma;
  if (canonicalMaSpelling(ma) === "S06" && input.priceUsd !== 25) {
    return { ok: false, error: "S06 stays $25." };
  }
  try {
    const next = productFromFields(ma, input);
    const updated = catalog.slice();
    updated[index] = next;
    assertUniqueNormalizedMas(updated);
    return { ok: true, products: updated, ma };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Save failed" };
  }
}

export function renameProductInCatalog(
  catalog: Product[],
  fromInput: string,
  toInput: string,
  input: ProductFieldsInput,
): CatalogMutation {
  const from = normalizeMa(fromInput);
  const to = normalizeMa(toInput);
  if (!isValidMa(from) || !isValidMa(to)) {
    return {
      ok: false,
      error:
        "New mã must be one allowed letter plus digits (example A03). Letters: A Q V K G B P H J S O D.",
    };
  }
  if (!isSellableMa(from) || !isSellableMa(to)) {
    return { ok: false, error: nonAllowlistSaveError(isSellableMa(to) ? from : to) };
  }
  if (from === to) {
    return saveProductInCatalog(catalog, from, input);
  }
  if (!isCanonicalMaSpelling(to)) {
    return { ok: false, error: `Use ${canonicalMaSpelling(to)}, not ${to}.` };
  }
  if (isOffLiveSell(to)) {
    return { ok: false, error: `Cannot change mã to ${to}.` };
  }
  if (to === "S06" && input.priceUsd !== 25) {
    return { ok: false, error: "S06 stays $25." };
  }
  if (isKnownSeedMa(canonicalMaSpelling(from))) {
    return {
      ok: false,
      error: `Cannot rename hub mã ${from}. Keep the ten. Add a new piece instead.`,
    };
  }
  const index = catalogIndex(catalog, from);
  if (index < 0) {
    return { ok: false, error: `Mã ${from} is not in the catalog` };
  }
  if (catalog.some((product, i) => i !== index && canonicalMaSpelling(product.ma) === to)) {
    return { ok: false, error: `Mã ${to} already exists. Do not gộp. Pick an unused mã.` };
  }
  try {
    const renamed = productFromFields(to, input);
    const updated = catalog.slice();
    updated[index] = renamed;
    assertUniqueNormalizedMas(updated);
    return { ok: true, products: updated, ma: to };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Change mã failed" };
  }
}

export function removeProductFromCatalog(catalog: Product[], maInput: string): CatalogMutation {
  const ma = normalizeMa(maInput);
  if (!ma) {
    return { ok: false, error: "Mã is required" };
  }
  const index = catalogIndex(catalog, ma);
  if (index < 0) {
    return { ok: false, error: `Mã ${ma} is not in the catalog` };
  }
  if (isKnownSeedMa(canonicalMaSpelling(ma))) {
    return {
      ok: false,
      error: `Cannot remove hub mã ${ma}. Mark Sold / Gone to hide it. Never invent a replacement mã.`,
    };
  }
  if (catalog.length <= 1) {
    return { ok: false, error: "Catalog must keep at least one mã" };
  }
  const updated = catalog.filter((_, i) => i !== index);
  return { ok: true, products: updated, ma };
}

export function bulkHoldInCatalog(catalog: Product[], mas: string[]): CatalogMutation {
  if (mas.length === 0) {
    return { ok: false, error: "Pick at least one mã" };
  }
  let products = catalog;
  let last = "";
  for (const raw of mas) {
    const current = products[catalogIndex(products, normalizeMa(raw))];
    if (!current) {
      return { ok: false, error: `Mã ${normalizeMa(raw)} is not in the catalog` };
    }
    const result = saveProductInCatalog(products, current.ma, {
      titleEn: current.titleEn,
      titleVn: current.titleVn,
      descriptionEn: current.descriptionEn,
      descriptionVn: current.descriptionVn,
      status: "hold",
      priceUsd: null,
      colors: current.colors,
      images: current.images,
      sizes: current.sizes,
      fitCm: current.fitCm,
      fulfillment: current.fulfillment,
      sourceLink: current.sourceLink,
    });
    if (!result.ok) {
      return result;
    }
    products = result.products;
    last = result.ma;
  }
  return { ok: true, products, ma: last };
}

export function mergeProductColors(
  catalog: Product[],
  maInput: string,
  keepId: string,
  dropId: string,
): CatalogMutation {
  const ma = normalizeMa(maInput);
  const current = catalog[catalogIndex(catalog, ma)];
  if (!current) {
    return { ok: false, error: `Mã ${ma} is not in the catalog` };
  }
  try {
    const merged = mergeColorAssets(current.colors, current.images, keepId, dropId);
    return saveProductInCatalog(catalog, current.ma, {
      titleEn: current.titleEn,
      titleVn: current.titleVn,
      descriptionEn: current.descriptionEn,
      descriptionVn: current.descriptionVn,
      status: current.status,
      priceUsd: current.priceUsd,
      colors: merged.colors,
      images: merged.images,
      sizes: current.sizes,
      fitCm: current.fitCm,
      fulfillment: current.fulfillment,
      sourceLink: current.sourceLink,
    });
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Color merge failed" };
  }
}
