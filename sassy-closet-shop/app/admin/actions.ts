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
import { normalizeMa } from "@/lib/ma";
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
