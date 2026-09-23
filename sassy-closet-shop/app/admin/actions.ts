"use server";

import { isAddLetter, mergeAddFields } from "@/lib/admin-add";
import {
  addProductToCatalog,
  bulkHoldInCatalog,
  fieldsFromProduct,
  removeProductFromCatalog,
  renameProductInCatalog,
  saveProductInCatalog,
  type ProductFieldsInput,
} from "@/lib/admin-ops";
import { emptyFitCm } from "@/lib/asia-size";
import { applyCatalogHandoff, settingsForHandoffImport, toHandoffCatalogJson } from "@/lib/catalog-handoff";
import {
  getCatalogStorageInfo,
  storageWriteErrorMessage,
  uploadCatalogImage,
} from "@/lib/catalog-store";
import { catalogExportFilename } from "@/lib/catalog-contract";
import { normalizeMa, isValidMa } from "@/lib/ma";
import {
  asCatalogDocument,
  assertCanonicalSerializedCatalog,
  parseCatalogDocument,
  toCatalogDocumentJson,
} from "@/lib/product-parse";
import { getCatalogDocumentUncached, getProductsUncached } from "@/lib/products";
import { commitCatalogDocument, commitProductList, type SaveReceipt } from "@/lib/save-commit";
import { assertImportSellContract, isSellableMa, nonAllowlistSaveError } from "@/lib/sell-contract";
import { parseSiteSettings } from "@/lib/site-settings";
import { siteId } from "@/lib/site-runtime";
import { uploadOverServerActionLimit, uploadTooLargeError } from "@/lib/upload-limits";
import {
  sanitizeIntakeSubmission,
  type IntakeSubmission,
} from "@/lib/intake-import";
import {
  isPipelineStageId,
  linkPipelineIntakeMa,
  setPipelineStage,
  type PipelineDocument,
} from "@/lib/pipeline";
import { readPipelineForAdmin, writePipelineRecord } from "@/lib/pipeline-store";

export type AdminActionResult = SaveReceipt | { ok: false; error: string };

function assertStorageWritable(): { ok: false; error: string } | null {
  if (!getCatalogStorageInfo().canWrite) {
    return { ok: false, error: storageWriteErrorMessage() };
  }
  return null;
}

function fieldsOf(input: ProductFieldsInput): ProductFieldsInput {
  return {
    titleEn: input.titleEn,
    titleVn: input.titleVn,
    descriptionEn: input.descriptionEn,
    descriptionVn: input.descriptionVn,
    status: input.status,
    priceUsd: input.priceUsd,
    colors: input.colors,
    images: input.images,
    sizes: input.sizes ?? [],
    fitCm: input.fitCm ?? emptyFitCm(),
    fulfillment: input.fulfillment,
    sourceLink: input.sourceLink ?? null,
  };
}

export async function saveProductAction(
  input: ProductFieldsInput & { ma: string },
): Promise<AdminActionResult> {
  try {
    const blocked = assertStorageWritable();
    if (blocked) {
      return blocked;
    }
    if (!isSellableMa(input.ma)) {
      return { ok: false, error: nonAllowlistSaveError(input.ma) };
    }
    const catalog = await getProductsUncached();
    const result = saveProductInCatalog(catalog, input.ma, fieldsOf(input));
    if (!result.ok) {
      return result;
    }
    return commitProductList(result.products, [result.ma], { ma: result.ma });
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Save failed" };
  }
}

export async function addProductAction(
  input: ProductFieldsInput & { letter: string },
): Promise<AdminActionResult> {
  try {
    const blocked = assertStorageWritable();
    if (blocked) {
      return blocked;
    }
    const letterRaw = typeof input.letter === "string" ? input.letter.trim().toUpperCase() : "";
    if (!isAddLetter(letterRaw)) {
      return {
        ok: false,
        error: "Pick a valid letter (A/Q/V/K/G/P/S/O/H/J/B/D). The mã is assigned on Save.",
      };
    }
    const catalog = await getProductsUncached();
    const result = addProductToCatalog(catalog, letterRaw, mergeAddFields(letterRaw, fieldsOf(input)));
    if (!result.ok) {
      return result;
    }
    return commitProductList(result.products, [result.ma], {
      ma: result.ma,
      nextMa: result.ma,
    });
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Add failed" };
  }
}

export async function renameProductAction(
  input: ProductFieldsInput & { from: string; to: string },
): Promise<AdminActionResult> {
  try {
    const blocked = assertStorageWritable();
    if (blocked) {
      return blocked;
    }
    if (!isSellableMa(input.from) || !isSellableMa(input.to)) {
      return { ok: false, error: nonAllowlistSaveError(isSellableMa(input.to) ? input.from : input.to) };
    }
    const catalog = await getProductsUncached();
    const result = renameProductInCatalog(catalog, input.from, input.to, fieldsOf(input));
    if (!result.ok) {
      return result;
    }
    return commitProductList(result.products, [input.from, result.ma], {
      ma: result.ma,
      renamedTo: result.ma,
    });
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Change mã failed" };
  }
}

export async function removeProductAction(ma: string): Promise<AdminActionResult> {
  try {
    const blocked = assertStorageWritable();
    if (blocked) {
      return blocked;
    }
    const catalog = await getProductsUncached();
    const result = removeProductFromCatalog(catalog, ma);
    if (!result.ok) {
      return result;
    }
    return commitProductList(result.products, [result.ma], { ma: result.ma });
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Remove failed" };
  }
}

export async function saveSettingsAction(input: {
  announcementLines: string[];
  facebookPageUrl: string;
}): Promise<AdminActionResult> {
  try {
    const blocked = assertStorageWritable();
    if (blocked) {
      return blocked;
    }
    const document = await getCatalogDocumentUncached();
    const settings = parseSiteSettings({
      announcementLines: input.announcementLines,
      facebookPageUrl: input.facebookPageUrl,
    });
    return commitCatalogDocument(
      asCatalogDocument(document.products, settings, document.siteId),
      document.products.map((product) => product.ma),
    );
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Settings save failed" };
  }
}

export async function exportCatalogAction(): Promise<
  { ok: true; json: string; filename: string } | { ok: false; error: string }
> {
  try {
    const document = await getCatalogDocumentUncached();
    return {
      ok: true,
      json: toHandoffCatalogJson(document),
      filename: catalogExportFilename(document.siteId || siteId()),
    };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Export failed" };
  }
}

export async function importCatalogAction(
  jsonText: string,
  mode: "replace" | "merge" = "replace",
): Promise<AdminActionResult> {
  try {
    const blocked = assertStorageWritable();
    if (blocked) {
      return blocked;
    }
    let raw: unknown;
    try {
      raw = JSON.parse(jsonText);
    } catch {
      return { ok: false, error: "Import file is not valid JSON." };
    }
    const live = await getCatalogDocumentUncached();
    const parsed = parseCatalogDocument(raw);
    const incoming = asCatalogDocument(parsed.products, parsed.settings, siteId());
    const next = applyCatalogHandoff(
      live,
      incoming,
      mode,
      settingsForHandoffImport(raw, live.settings, incoming.settings),
    );
    assertImportSellContract(next.products);
    assertCanonicalSerializedCatalog(toCatalogDocumentJson(next));
    return commitCatalogDocument(
      next,
      next.products.map((product) => product.ma),
    );
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Import failed" };
  }
}

export async function bulkHoldAction(mas: string[]): Promise<AdminActionResult> {
  try {
    const blocked = assertStorageWritable();
    if (blocked) {
      return blocked;
    }
    for (const ma of mas) {
      if (!isSellableMa(ma)) {
        return { ok: false, error: nonAllowlistSaveError(ma) };
      }
    }
    const catalog = await getProductsUncached();
    const result = bulkHoldInCatalog(catalog, mas);
    if (!result.ok) {
      return result;
    }
    return commitProductList(result.products, mas, { ma: result.ma });
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Bulk Hold failed" };
  }
}

export async function uploadImageAction(
  ma: string,
  formData: FormData,
): Promise<{ ok: true; url: string } | { ok: false; error: string }> {
  try {
    if (!getCatalogStorageInfo().canUpload) {
      return {
        ok: false,
        error: "Uploads need BLOB_READ_WRITE_TOKEN. You can still paste an image URL.",
      };
    }
    const file = formData.get("file");
    if (!(file instanceof File) || file.size === 0) {
      return { ok: false, error: "Choose an image file" };
    }
    if (uploadOverServerActionLimit(file.size)) {
      return { ok: false, error: uploadTooLargeError(file.size) };
    }
    if (file.type && !file.type.startsWith("image/")) {
      return { ok: false, error: "File must be an image" };
    }
    const normalized = normalizeMa(ma);
    if (!isSellableMa(normalized)) {
      return { ok: false, error: nonAllowlistSaveError(normalized) };
    }
    const url = await uploadCatalogImage(normalized, file);
    return { ok: true, url };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Upload failed" };
  }
}

export { fieldsFromProduct };

/**
 * Intake site base URL. The intake app (sassy-closet) stages submissions in
 * its own store — this sell-site app does not share it, so staged rows are
 * pulled over the intake site's public /api/submissions (server-side fetch).
 * Override with INTAKE_SITE_URL when the intake app moves.
 */
function intakeSiteBase(): string {
  const raw = (process.env.INTAKE_SITE_URL ?? "https://sassy-closet.vercel.app").trim();
  return raw.replace(/\/+$/, "");
}

export async function fetchIntakeStagedAction(): Promise<
  { ok: true; items: IntakeSubmission[] } | { ok: false; error: string }
> {
  const base = intakeSiteBase();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${base}/api/submissions`, {
      cache: "no-store",
      signal: controller.signal,
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      return {
        ok: false,
        error: `Intake site answered ${response.status}. It may be redeploying — try again, or paste the submission JSON below.`,
      };
    }
    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      return { ok: false, error: "Intake site returned unreadable data. Paste the submission JSON below instead." };
    }
    const list =
      typeof payload === "object" && payload !== null && Array.isArray((payload as { submissions?: unknown }).submissions)
        ? ((payload as { submissions: unknown[] }).submissions)
        : [];
    const items: IntakeSubmission[] = [];
    for (const entry of list) {
      const submission = sanitizeIntakeSubmission(entry);
      if (submission && submission.status === "staged") {
        items.push(submission);
      }
    }
    items.sort((a, b) => b.updated_at.localeCompare(a.updated_at));
    return { ok: true, items };
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      return { ok: false, error: "Intake site timed out after 15s. Paste the submission JSON below instead." };
    }
    return {
      ok: false,
      error: `Could not reach the intake site (${error instanceof Error ? error.message : "fetch failed"}). Paste the submission JSON below instead.`,
    };
  } finally {
    clearTimeout(timer);
  }
}

export type PipelineActionResult =
  | { ok: true; pipeline: PipelineDocument }
  | { ok: false; error: string };

export async function getPipelineAction(): Promise<PipelineActionResult> {
  try {
    return { ok: true, pipeline: await readPipelineForAdmin() };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Pipeline read failed" };
  }
}

/**
 * Toggle one pipeline stage for a mã. Draft-only bookkeeping — it never
 * touches products, prices, or Square. Requires a writable store.
 */
export async function setPipelineStageAction(
  ma: string,
  stage: string,
  done: boolean,
): Promise<PipelineActionResult> {
  try {
    const blocked = assertStorageWritable();
    if (blocked) {
      return blocked;
    }
    const target = normalizeMa(ma);
    if (!isValidMa(target)) {
      return { ok: false, error: `Not a valid mã: ${ma}. Never invent one.` };
    }
    if (!isPipelineStageId(stage)) {
      return { ok: false, error: `Unknown pipeline stage: ${stage}.` };
    }
    const current = await readPipelineForAdmin();
    const next = setPipelineStage(current, target, stage, done);
    const saved = await writePipelineRecord(next);
    return { ok: true, pipeline: saved };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Pipeline save failed" };
  }
}

/**
 * Link an intake-minted mã to its sell-site mã on the tracker row, after an
 * intake draft is saved under the sell site's assigned code.
 */
export async function linkPipelineIntakeAction(
  ma: string,
  intakeMa: string,
): Promise<PipelineActionResult> {
  try {
    const blocked = assertStorageWritable();
    if (blocked) {
      return blocked;
    }
    const target = normalizeMa(ma);
    const intake = normalizeMa(intakeMa);
    if (!isValidMa(target) || !isValidMa(intake)) {
      return { ok: false, error: "Link needs two valid mãs. Never invent one." };
    }
    const current = await readPipelineForAdmin();
    const saved = await writePipelineRecord(linkPipelineIntakeMa(current, target, intake));
    return { ok: true, pipeline: saved };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Pipeline link failed" };
  }
}
