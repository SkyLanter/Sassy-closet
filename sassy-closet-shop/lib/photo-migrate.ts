/**
 * Migrate external product cover URLs (Catbox, Alicdn, etc.) to Vercel Blob.
 *
 * Problem: D05 used a Catbox cover and V03 used an Alicdn cover in the live
 * catalog. External hosts go blank; Blob URLs persist through GitHub deploys.
 *
 * The migration fetches each external image, uploads it to Blob under the
 * product's catalog image prefix, and rewrites the product's image src to the
 * Blob URL. Blob-first: after migration, covers are Blob URLs, never external.
 */

import { createHash } from "node:crypto";
import { catalogImagePrefix } from "@/lib/catalog-contract";
import type { CatalogDocument, Product, ProductImageAsset } from "@/lib/types";

/** Binary upload port — mirrors the BlobCatalogPort pattern for images. */
export type ImageBlobPort = {
  putImage(pathname: string, bytes: Buffer, contentType: string): Promise<{ url: string }>;
};

export type FetchImageFn = (url: string) => Promise<{ bytes: Buffer; contentType: string }>;

export type MigratedCover = {
  ma: string;
  from: string;
  to: string;
};

export type PhotoMigrateReport = {
  migrated: MigratedCover[];
  skipped: { ma: string; src: string; reason: string }[];
  errors: { ma: string; src: string; error: string }[];
};

/**
 * True for http(s) URLs that are NOT already on Blob or the shop's own paths.
 * Local /products/, /uploads/, and data: URLs are left alone.
 */
export function isExternalCoverUrl(src: string): boolean {
  const trimmed = src.trim();
  if (!trimmed) {
    return false;
  }
  if (trimmed.startsWith("data:")) {
    return false;
  }
  if (!/^https?:\/\//i.test(trimmed)) {
    return false;
  }
  try {
    const url = new URL(trimmed);
    const host = url.hostname.toLowerCase();
    // Already on Vercel Blob — Blob-first, nothing to do.
    if (host.includes("blob.vercel-storage.com") || host.includes("public.blob.vercel-storage.com")) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

function imageFileName(ma: string, fromUrl: string, bytes: Buffer, contentType: string): string {
  const digest = createHash("sha256").update(bytes).digest("hex").slice(0, 12);
  let ext = "jpg";
  const ct = contentType.toLowerCase();
  if (ct.includes("png")) ext = "png";
  else if (ct.includes("webp")) ext = "webp";
  else if (ct.includes("gif")) ext = "gif";
  else {
    const match = fromUrl.split("?")[0]?.match(/\.([a-z0-9]{2,5})$/i);
    if (match?.[1]) {
      const candidate = match[1].toLowerCase();
      if (["jpg", "jpeg", "png", "webp", "gif"].includes(candidate)) {
        ext = candidate === "jpeg" ? "jpg" : candidate;
      }
    }
  }
  return `migrated-${digest}.${ext}`;
}

function contentTypeFor(bytes: Buffer, declared: string): string {
  if (declared && declared !== "application/octet-stream") {
    return declared;
  }
  // Magic bytes sniff — never trust the extension alone.
  if (bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) {
    return "image/jpeg";
  }
  if (
    bytes.length >= 8 &&
    bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47
  ) {
    return "image/png";
  }
  if (bytes.length >= 12 && bytes.subarray(0, 4).toString() === "RIFF" && bytes.subarray(8, 12).toString() === "WEBP") {
    return "image/webp";
  }
  if (bytes.length >= 6 && bytes.subarray(0, 6).toString().startsWith("GIF")) {
    return "image/gif";
  }
  return declared || "application/octet-stream";
}

async function migrateProductImages(
  product: Product,
  port: ImageBlobPort,
  fetchImage: FetchImageFn,
  report: PhotoMigrateReport,
): Promise<Product> {
  const images: ProductImageAsset[] = [];
  for (const image of product.images) {
    if (!isExternalCoverUrl(image.src)) {
      images.push(image);
      continue;
    }
    try {
      const fetched = await fetchImage(image.src);
      if (fetched.bytes.length === 0) {
        report.skipped.push({ ma: product.ma, src: image.src, reason: "empty bytes" });
        images.push(image);
        continue;
      }
      const contentType = contentTypeFor(fetched.bytes, fetched.contentType);
      const filename = imageFileName(product.ma, image.src, fetched.bytes, contentType);
      const pathname = `${catalogImagePrefix(product.ma)}/${filename}`;
      const { url } = await port.putImage(pathname, fetched.bytes, contentType);
      if (!url) {
        report.errors.push({ ma: product.ma, src: image.src, error: "Blob put returned no URL" });
        images.push(image);
        continue;
      }
      report.migrated.push({ ma: product.ma, from: image.src, to: url });
      images.push({ ...image, src: url });
    } catch (error) {
      const detail = error instanceof Error ? error.message : "fetch/upload failed";
      report.errors.push({ ma: product.ma, src: image.src, error: detail });
      // Keep the original src on failure — never blank a cover.
      images.push(image);
    }
  }
  return { ...product, images };
}

/**
 * Migrate every external cover URL in the catalog to Blob.
 * Never invents mã or products — only rewrites image srcs.
 * On failure the original src is kept, so covers never go blank.
 */
export async function migrateExternalCoversToBlob(
  document: CatalogDocument,
  port: ImageBlobPort,
  fetchImage: FetchImageFn,
): Promise<{ document: CatalogDocument; report: PhotoMigrateReport }> {
  const report: PhotoMigrateReport = { migrated: [], skipped: [], errors: [] };
  const products: Product[] = [];
  for (const product of document.products) {
    products.push(await migrateProductImages(product, port, fetchImage, report));
  }
  return {
    document: { ...document, products },
    report,
  };
}

/** Default fetch implementation — 15s timeout, follows redirects. */
export async function fetchImageBytes(url: string): Promise<{ bytes: Buffer; contentType: string }> {
  const response = await fetch(url, {
    signal: AbortSignal.timeout(15_000),
    headers: { "User-Agent": "SassyCloset/1.0 (cover-migration)" },
  });
  if (!response.ok) {
    throw new Error(`fetch failed (${response.status})`);
  }
  const contentType = response.headers.get("content-type")?.split(";")[0]?.trim() ?? "";
  const bytes = Buffer.from(await response.arrayBuffer());
  return { bytes, contentType };
}
