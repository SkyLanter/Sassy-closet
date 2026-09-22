import type { ProductFieldsInput } from "@/lib/admin-ops";

function asRecord(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return {};
  }
  return value as Record<string, unknown>;
}

export function mergeItemFieldsFromBody(
  body: unknown,
  fallback: ProductFieldsInput,
): ProductFieldsInput {
  const row = asRecord(body);
  return {
    titleEn: typeof row.titleEn === "string" ? row.titleEn : fallback.titleEn,
    titleVn: typeof row.titleVn === "string" ? row.titleVn : fallback.titleVn,
    descriptionEn: typeof row.descriptionEn === "string" ? row.descriptionEn : fallback.descriptionEn,
    descriptionVn: typeof row.descriptionVn === "string" ? row.descriptionVn : fallback.descriptionVn,
    status: typeof row.status === "string" ? row.status : fallback.status,
    priceUsd:
      row.priceUsd === undefined
        ? fallback.priceUsd
        : row.priceUsd === null || typeof row.priceUsd === "number"
          ? row.priceUsd
          : fallback.priceUsd,
    colors: Array.isArray(row.colors) ? (row.colors as ProductFieldsInput["colors"]) : fallback.colors,
    images: Array.isArray(row.images) ? (row.images as ProductFieldsInput["images"]) : fallback.images,
    sizes: Array.isArray(row.sizes) ? (row.sizes as ProductFieldsInput["sizes"]) : fallback.sizes,
    fitCm:
      row.fitCm && typeof row.fitCm === "object" && !Array.isArray(row.fitCm)
        ? (row.fitCm as ProductFieldsInput["fitCm"])
        : fallback.fitCm,
    fulfillment:
      typeof row.fulfillment === "string"
        ? (row.fulfillment as ProductFieldsInput["fulfillment"])
        : fallback.fulfillment,
    sourceLink:
      row.sourceLink === undefined
        ? fallback.sourceLink
        : typeof row.sourceLink === "string" || row.sourceLink === null
          ? row.sourceLink
          : fallback.sourceLink,
  };
}
