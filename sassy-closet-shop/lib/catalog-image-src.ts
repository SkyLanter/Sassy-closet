import { isOffLiveSell } from "@/lib/held-incomplete";

/**
 * How a catalog image src relates to a `/products/{folder}/` path.
 * Absolute Blob URLs count. Dots and percent-encoding are resolved first.
 */
type CatalogImageFolder = "clear" | "off-live" | "unsafe";

function pathnameOf(src: string): string | null {
  const trimmed = src.trim();
  if (!trimmed) {
    return "";
  }
  if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
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

export function catalogImageFolder(src: string): CatalogImageFolder {
  const pathname = pathnameOf(src);
  if (pathname === null) {
    return "unsafe";
  }
  if (pathname === "") {
    return "clear";
  }
  const segments = normalizedSegments(pathname);
  if (segments === null) {
    return "unsafe";
  }
  for (let index = 0; index < segments.length - 1; index += 1) {
    const marker = segments[index];
    const folder = segments[index + 1];
    if (!marker || !folder || marker.toLowerCase() !== "products") {
      continue;
    }
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
