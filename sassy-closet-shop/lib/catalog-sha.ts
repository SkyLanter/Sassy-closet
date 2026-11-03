import { createHash } from "node:crypto";
import { toCatalogDocumentJson } from "@/lib/product-parse";
import type { CatalogDocument } from "@/lib/types";

export function catalogShaOf(document: CatalogDocument): string {
  return createHash("sha256").update(toCatalogDocumentJson(document)).digest("hex");
}

export function shortCatalogSha(document: CatalogDocument): string {
  return catalogShaOf(document).slice(0, 12);
}

/** Append or replace ?v= so a CDN HIT of the same pathname cannot stick. */
export function cacheBustMediaSrc(src: string, version: string): string {
  const trimmed = src.trim();
  const token = version.trim();
  if (!trimmed || !token) {
    return trimmed;
  }
  if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
    try {
      const url = new URL(trimmed);
      url.searchParams.set("v", token);
      return url.toString();
    } catch {
      // Fall through to query-string rewrite.
    }
  }
  const hashIndex = trimmed.indexOf("#");
  const hash = hashIndex >= 0 ? trimmed.slice(hashIndex) : "";
  const withoutHash = hashIndex >= 0 ? trimmed.slice(0, hashIndex) : trimmed;
  const qIndex = withoutHash.indexOf("?");
  const path = qIndex >= 0 ? withoutHash.slice(0, qIndex) : withoutHash;
  const params = new URLSearchParams(qIndex >= 0 ? withoutHash.slice(qIndex + 1) : "");
  params.set("v", token);
  return `${path}?${params.toString()}${hash}`;
}

export function shopCoverSrc(ma: string, version: string): string {
  return cacheBustMediaSrc(`/products/${ma}/cover.jpg`, version);
}

export function isInPlaceCoverPath(pathname: string): boolean {
  return /(?:^|\/)cover\.jpe?g$/i.test(pathname) && !/cover-[a-f0-9]{8,}\./i.test(pathname);
}
