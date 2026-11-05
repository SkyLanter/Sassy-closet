import { isOffLiveSell } from "@/lib/held-incomplete";

/**
 * How a catalog image src relates to a `/products/{folder}/` path.
 * Absolute Blob URLs count. Tabs and newlines are removed first, the same
 * way a browser parses an img src, then dots and percent-encoding.
 */
type CatalogImageFolder = "clear" | "off-live" | "unsafe";

function pathnameOf(src: string): string | null {
  const trimmed = src.trim().replace(/[\t\r\n]/g, "");
  if (!trimmed) {
    return "";
  }
  if (/^https?:\/\//i.test(trimmed)) {
    try {
      return new URL(trimmed).pathname;
    } catch {
      return null;
    }
  }
  const noHash = trimmed.split("#")[0] ?? trimmed;
  return noHash.split("?")[0] ?? noHash;
}

/** Lexical path segments. `..` that escapes the root is unsafe. */
function normalizedSegments(pathname: string): string[] | null {
  const segments: string[] = [];
  for (const raw of pathname.split("/")) {
    if (raw === "" || raw === ".") {
      continue;
    }
    let segment: string;
    try {
      segment = decodeURIComponent(raw);
    } catch {
      return null;
    }
    if (segment === "" || segment === ".") {
      continue;
    }
    if (segment === "..") {
      if (segments.length === 0) {
        return null;
      }
      segments.pop();
      continue;
    }
    if (segment.includes("/") || segment.includes("\\") || segment.includes("\0") || segment.includes("..")) {
      return null;
    }
    segments.push(segment);
  }
  return segments;
}

/**
 * Folders that sit under a `products` segment after one decode and dot-segment collapse.
 * Null when the path is unsafe. Empty when the src has no product folder.
 */
export function catalogProductFolders(src: string): string[] | null {
  const pathname = pathnameOf(src);
  if (pathname === null) {
    return null;
  }
  if (pathname === "") {
    return [];
  }
  const segments = normalizedSegments(pathname);
  if (segments === null) {
    return null;
  }
  const folders: string[] = [];
  for (let index = 0; index < segments.length - 1; index += 1) {
    const marker = segments[index];
    const folder = segments[index + 1];
    if (!marker || !folder || marker.toLowerCase() !== "products") {
      continue;
    }
    folders.push(folder);
  }
  return folders;
}

export function catalogImageFolder(src: string): CatalogImageFolder {
  const folders = catalogProductFolders(src);
  if (folders === null) {
    return "unsafe";
  }
  for (const folder of folders) {
    if (isOffLiveSell(folder)) {
      return "off-live";
    }
  }
  return "clear";
}

/** True when this src must not be read or fetched by the public image route. */
export function catalogImageSrcBlocked(src: string): boolean {
  const decision = catalogImageFolder(src);
  switch (decision) {
    case "clear":
      return false;
    case "off-live":
    case "unsafe":
      return true;
    default: {
      const neverDecision: never = decision;
      return neverDecision;
    }
  }
}
