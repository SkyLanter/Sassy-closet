import { CATALOG_SCHEMA } from "@/lib/catalog-contract";

function parseObject(json: string, invalid: string): Record<string, unknown> {
  const trimmed = json.trim();
  if (!trimmed || trimmed.startsWith("<")) {
    throw new Error(invalid);
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(json) as unknown;
  } catch {
    throw new Error(invalid);
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error("Handoff catalog must be a catalog.v1 object");
  }
  return parsed as Record<string, unknown>;
}

/** Kit / official import: schema + products. Excel `source` is allowed (photos already dropped in parse). */
export function assertImportableHandoffJson(json: string): unknown {
  const row = parseObject(json, "Import file is not valid catalog.v1 JSON.");
  if (row.schema !== CATALOG_SCHEMA) {
    throw new Error("Handoff catalog must set schema catalog.v1");
  }
  if (!Array.isArray(row.products)) {
    throw new Error("Handoff catalog must include products");
  }
  return row;
}

/** Shop export download: catalog.v1, allowlist, no HTML, no OneDrive xlsx path. */
export function assertHandoffExportText(json: string): void {
  const row = parseObject(json, "Export did not return catalog.v1 JSON.");
  if (row.schema !== CATALOG_SCHEMA) {
    throw new Error("Handoff catalog must set schema catalog.v1");
  }
  if (!Array.isArray(row.products) || row.products.length === 0) {
    throw new Error("Handoff catalog must include products");
  }
  if (!Array.isArray(row.allowlist)) {
    throw new Error("Handoff catalog must include the ten-mã allowlist");
  }
  if (typeof row.source === "string" && /sassycloset\.xlsx/i.test(row.source)) {
    throw new Error("Shop export must not write the OneDrive xlsx path");
  }
}
