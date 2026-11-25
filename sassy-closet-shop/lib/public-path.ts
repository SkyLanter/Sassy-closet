import path from "node:path";

/**
 * Absolute file under `public/` for a same-origin src.
 * Null when the src is not a local path or would leave that folder (`..`, null bytes).
 */
export function resolvedPublicFile(src: string): string | null {
  const pathOnly = (src.split("?")[0] ?? "").trim();
  if (!pathOnly.startsWith("/") || pathOnly.startsWith("//")) {
    return null;
  }
  let decoded: string;
  try {
    decoded = decodeURIComponent(pathOnly);
  } catch {
    return null;
  }
  if (decoded.includes("\0") || decoded.split(/[/\\]/).includes("..")) {
    return null;
  }
  const publicRoot = path.resolve(process.cwd(), "public");
  const resolved = path.resolve(publicRoot, decoded.replace(/^[/\\]+/, ""));
  const root = publicRoot.endsWith(path.sep) ? publicRoot : publicRoot + path.sep;
  if (resolved !== publicRoot && !resolved.startsWith(root)) {
    return null;
  }
  return resolved;
}
