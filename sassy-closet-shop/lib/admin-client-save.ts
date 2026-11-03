import { assertHandoffExportText } from "@/lib/handoff-json";
import { isCompleteSaveReceipt, receiptRevalidatedShop, silentSaveError, type SaveReceiptView } from "@/lib/save-receipt";
import type { ProductFieldsInput } from "@/lib/admin-ops";
import { maLetter } from "@/lib/ma";
import { isOpaqueRscError, opaquePostSaveMessage, publicSaveErrorMessage } from "@/lib/opaque-rsc-error";
import type { Product, SiteSettings } from "@/lib/types";

export type ClientSaveReceipt = SaveReceiptView & {
  ma: string;
  nextMa?: string;
  renamedTo?: string;
  products?: Product[];
  settings?: SiteSettings;
};

export type CatalogSnapshot = {
  products: Product[];
  catalogSha: string;
  updatedAt: string | null;
};

const JSON_HEADERS = {
  Accept: "application/json",
  "Cache-Control": "no-cache",
  Pragma: "no-cache",
} as const;

function coerceTrue(value: unknown): boolean {
  return value === true || value === "true" || value === 1;
}

export function normalizeReceiptShape(value: unknown): unknown {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return value;
  }
  const row = { ...(value as Record<string, unknown>) };
  if (coerceTrue(row.ok)) {
    row.ok = true;
  }
  if (coerceTrue(row.blobWritten)) {
    row.blobWritten = true;
  }
  if (typeof row.revalidated === "string") {
    row.revalidated = row.revalidated
      .split(",")
      .map((path) => path.trim())
      .filter((path) => path.length > 0);
  }
  return row;
}

export function parseAdminJsonResponse(text: string, status: number): unknown {
  const trimmed = text.trim();
  if (!trimmed) {
    return { ok: false, error: `Save returned an empty HTTP ${status} body.` };
  }
  try {
    return JSON.parse(trimmed) as unknown;
  } catch {
    if (isOpaqueRscError(trimmed)) {
      return { ok: false, error: opaquePostSaveMessage() };
    }
    return { ok: false, error: `Save returned HTTP ${status} that was not JSON.` };
  }
}

export function isRecoverableSaveTransportError(error: string): boolean {
  if (isOpaqueRscError(error)) {
    return true;
  }
  return /empty HTTP|not JSON|did not return|failed to fetch|network error|Load failed|Save request failed|text\/x-component|Save failed\.?$|HTTP 5\d\d|HTTP 408|HTTP 429/i.test(
    error,
  );
}

export function liveProductReflectsFields(product: Product, fields: ProductFieldsInput): boolean {
  const expectedPrice = fields.status === "hold" ? null : fields.priceUsd;
  return (
    product.titleEn === fields.titleEn &&
    product.titleVn === fields.titleVn &&
    product.descriptionEn === fields.descriptionEn &&
    product.descriptionVn === fields.descriptionVn &&
    product.status === fields.status &&
    product.priceUsd === expectedPrice
  );
}

async function postJson(path: string, body: unknown): Promise<unknown> {
  try {
    const response = await fetch(path, {
      method: "POST",
      cache: "no-store",
      credentials: "same-origin",
      headers: {
        ...JSON_HEADERS,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
    const text = await response.text();
    return parseAdminJsonResponse(text, response.status);
  } catch (error) {
    return {
      ok: false,
      error: publicSaveErrorMessage(error, "Save request failed. Check the network and try again."),
    };
  }
}

function asSettings(value: unknown): SiteSettings | undefined {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return undefined;
  }
  const row = value as Record<string, unknown>;
  if (!Array.isArray(row.announcementLines) || typeof row.facebookPageUrl !== "string") {
    return undefined;
  }
  return {
    announcementLines: row.announcementLines.filter(
      (line): line is string => typeof line === "string",
    ),
    facebookPageUrl: row.facebookPageUrl,
  };
}

function asReceipt(
  value: unknown,
  options?: { requireMa?: boolean; requireCatalog?: boolean; requireShop?: boolean },
): ClientSaveReceipt | { ok: false; error: string } {
  const normalized = normalizeReceiptShape(value);
  if (typeof normalized !== "object" || normalized === null) {
    return { ok: false, error: "Save did not return JSON." };
  }
  const row = normalized as Record<string, unknown>;
  if (row.ok === false) {
    return {
      ok: false,
      error: typeof row.error === "string" && row.error.trim() ? row.error : "Save failed.",
    };
  }
  if (!isCompleteSaveReceipt(normalized)) {
    return { ok: false, error: silentSaveError() };
  }
  const ma = typeof row.ma === "string" ? row.ma : typeof row.nextMa === "string" ? row.nextMa : "";
  if (options?.requireMa !== false && !ma) {
    return { ok: false, error: "Save receipt is missing the assigned mã." };
  }
  const products = Array.isArray(row.products) ? (row.products as Product[]) : undefined;
  const settings = asSettings(row.settings);
  if (options?.requireCatalog && (!products || !settings)) {
    return { ok: false, error: "Save receipt is missing the live catalog." };
  }
  if (options?.requireShop && !receiptRevalidatedShop(normalized as SaveReceiptView)) {
    return { ok: false, error: "Save wrote the catalog but did not revalidate the shop." };
  }
  return {
    ...(normalized as SaveReceiptView),
    ma,
    nextMa: typeof row.nextMa === "string" ? row.nextMa : undefined,
    renamedTo: typeof row.renamedTo === "string" ? row.renamedTo : undefined,
    products,
    settings,
  };
}

export async function postAdminAdd(
  input: ProductFieldsInput & { letter: string },
): Promise<ClientSaveReceipt | { ok: false; error: string }> {
  return asReceipt(await postJson("/api/admin/add", input));
}

export async function postAdminSave(
  input: ProductFieldsInput & { ma: string },
): Promise<ClientSaveReceipt | { ok: false; error: string }> {
  const posted = asReceipt(await postJson("/api/admin/save", input));
  if (posted.ok) {
    return posted;
  }
  if (!isRecoverableSaveTransportError(posted.error)) {
    return posted;
  }
  const recovered = await recoverExistingMaSave(input.ma, input);
  if (recovered) {
    return recovered;
  }
  return posted;
}

export async function postAdminRename(
  input: ProductFieldsInput & { from: string; to: string },
): Promise<ClientSaveReceipt | { ok: false; error: string }> {
  return asReceipt(await postJson("/api/admin/rename", input), { requireCatalog: true });
}

export async function postAdminRemove(
  ma: string,
): Promise<ClientSaveReceipt | { ok: false; error: string }> {
  return asReceipt(await postJson("/api/admin/remove", { ma }), { requireCatalog: true });
}

export async function postAdminSettings(input: {
  announcementLines: string[];
  facebookPageUrl: string;
}): Promise<ClientSaveReceipt | { ok: false; error: string }> {
  return asReceipt(await postJson("/api/admin/settings", input), {
    requireMa: false,
    requireCatalog: true,
    requireShop: true,
  });
}

export async function postAdminHold(
  mas: string[],
): Promise<ClientSaveReceipt | { ok: false; error: string }> {
  return asReceipt(await postJson("/api/admin/hold", { mas }), {
    requireMa: false,
    requireCatalog: true,
  });
}

export async function postAdminImport(
  catalog: unknown,
  mode: "replace" | "merge",
): Promise<ClientSaveReceipt | { ok: false; error: string }> {
  return asReceipt(await postJson("/api/admin/catalog/import", { catalog, mode }), {
    requireMa: false,
    requireCatalog: true,
    requireShop: true,
  });
}

export async function fetchCatalogExport(): Promise<
  { ok: true; json: string; filename: string } | { ok: false; error: string }
> {
  const response = await fetch("/api/admin/catalog/export", {
    cache: "no-store",
    credentials: "same-origin",
    headers: JSON_HEADERS,
  });
  if (!response.ok) {
    return { ok: false, error: `Export failed (HTTP ${response.status}).` };
  }
  const json = await response.text();
  try {
    assertHandoffExportText(json);
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : "Export did not return catalog.v1 JSON.",
    };
  }
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const match = disposition.match(/filename="([^"]+)"/);
  return { ok: true, json, filename: match?.[1] ?? "catalog.v1.json" };
}

export async function fetchCatalogSnapshot(): Promise<CatalogSnapshot | null> {
  try {
    const response = await fetch("/api/admin/catalog", {
      cache: "no-store",
      credentials: "same-origin",
      headers: JSON_HEADERS,
    });
    const text = await response.text();
    if (!response.ok) {
      return null;
    }
    const body = JSON.parse(text) as {
      products?: Product[];
      catalogSha?: unknown;
      updatedAt?: unknown;
    };
    if (!Array.isArray(body.products) || typeof body.catalogSha !== "string") {
      return null;
    }
    return {
      products: body.products,
      catalogSha: body.catalogSha,
      updatedAt: typeof body.updatedAt === "string" ? body.updatedAt : null,
    };
  } catch {
    return null;
  }
}

export async function fetchCatalogMas(): Promise<string[]> {
  const snapshot = await fetchCatalogSnapshot();
  if (!snapshot) {
    return [];
  }
  return snapshot.products
    .map((row) => (typeof row?.ma === "string" ? row.ma : ""))
    .filter((ma) => ma.length > 0);
}

/** After a #441, Blob may already hold the new mã even though the action flight died. */
export async function recoverAddedMa(previousMas: string[], letter: string): Promise<string | null> {
  const live = await fetchCatalogMas();
  const previous = new Set(previousMas);
  const added = live.filter((ma) => !previous.has(ma) && maLetter(ma) === letter);
  if (added.length === 0) {
    return null;
  }
  return added.sort()[added.length - 1] ?? null;
}

/** After an opaque Edit Save response, Blob may already hold the fields. */
export async function recoverExistingMaSave(
  ma: string,
  fields: ProductFieldsInput,
): Promise<ClientSaveReceipt | null> {
  const snapshot = await fetchCatalogSnapshot();
  if (!snapshot || snapshot.catalogSha.length < 8) {
    return null;
  }
  const product = snapshot.products.find((row) => row.ma === ma);
  if (!product || !liveProductReflectsFields(product, fields)) {
    return null;
  }
  const updatedAt =
    snapshot.updatedAt && snapshot.updatedAt.length >= 8
      ? snapshot.updatedAt
      : new Date().toISOString();
  return {
    ok: true,
    ma,
    blobWritten: true,
    catalogSha: snapshot.catalogSha,
    updatedAt,
    revalidated: [`/m/${ma}`],
    products: snapshot.products,
  };
}
