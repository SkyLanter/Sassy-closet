import { readFile } from "node:fs/promises";
import path from "node:path";

const SHARE_PHOTO_TIMEOUT_MS = 3000;
const SHARE_PHOTO_MAX_BYTES = 7_000_000;
const LOCAL_ROOTS = ["products/", "uploads/", "editorial/"] as const;

export type SharePhoto = {
  data: Uint8Array;
  mime: "image/jpeg" | "image/png";
};

export type LoadSharePhotoOptions = {
  requestUrl?: string;
  fetchImpl?: typeof fetch;
};

export function sharePhotoFromBytes(bytes: Uint8Array): SharePhoto | null {
  if (bytes.byteLength < 8 || bytes.byteLength > SHARE_PHOTO_MAX_BYTES) {
    return null;
  }
  if (bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) {
    return { data: bytes, mime: "image/jpeg" };
  }
  if (
    bytes[0] === 0x89 &&
    bytes[1] === 0x50 &&
    bytes[2] === 0x4e &&
    bytes[3] === 0x47
  ) {
    return { data: bytes, mime: "image/png" };
  }
  return null;
}

export function localPublicPath(src: string): string | null {
  const trimmed = src.trim();
  if (!trimmed.startsWith("/") || trimmed.startsWith("//")) {
    return null;
  }
  const pathOnly = trimmed.split("?")[0]?.split("#")[0] ?? "";
  if (pathOnly.includes("..") || pathOnly.includes("\\")) {
    return null;
  }
  const relative = pathOnly.replace(/^\/+/, "");
  if (!LOCAL_ROOTS.some((root) => relative.startsWith(root))) {
    return null;
  }
  const publicRoot = path.resolve(process.cwd(), "public");
  const absolute = path.resolve(publicRoot, relative);
  if (!absolute.startsWith(`${publicRoot}${path.sep}`)) {
    return null;
  }
  return absolute;
}

function hostOf(raw: string | undefined): string | null {
  if (!raw) {
    return null;
  }
  try {
    if (raw.startsWith("http://") || raw.startsWith("https://")) {
      return new URL(raw).host.toLowerCase();
    }
    return raw.replace(/\/.*$/, "").toLowerCase();
  } catch {
    return null;
  }
}

/** Preview deployments are password-protected. Never fetch our own origin for a photo. */
export function isSelfHostedUrl(url: URL, requestUrl?: string): boolean {
  const hosts = new Set<string>();
  for (const raw of [
    requestUrl,
    process.env.VERCEL_URL,
    process.env.VERCEL_PROJECT_PRODUCTION_URL,
    process.env.NEXT_PUBLIC_SHOP_URL,
    process.env.SHOP_PUBLIC_URL,
  ]) {
    const host = hostOf(raw);
    if (host) {
      hosts.add(host);
    }
  }
  return hosts.has(url.host.toLowerCase());
}

async function readLocal(src: string): Promise<SharePhoto | null> {
  const file = localPublicPath(src);
  if (!file) {
    return null;
  }
  try {
    return sharePhotoFromBytes(new Uint8Array(await readFile(file)));
  } catch {
    return null;
  }
}

export async function loadSharePhoto(
  src: string | undefined,
  options: LoadSharePhotoOptions = {},
): Promise<SharePhoto | null> {
  const trimmed = src?.trim() ?? "";
  if (!trimmed) {
    return null;
  }
  try {
    if (trimmed.startsWith("/")) {
      return await readLocal(trimmed);
    }
    let url: URL;
    try {
      url = new URL(trimmed);
    } catch {
      return null;
    }
    if (url.protocol !== "https:" && url.protocol !== "http:") {
      return null;
    }
    if (isSelfHostedUrl(url, options.requestUrl)) {
      return await readLocal(`${url.pathname}${url.search}`);
    }
    const fetchImpl = options.fetchImpl ?? fetch;
    const response = await fetchImpl(url, {
      redirect: "follow",
      signal: AbortSignal.timeout(SHARE_PHOTO_TIMEOUT_MS),
    });
    if (!response.ok) {
      return null;
    }
    const length = Number(response.headers.get("content-length") ?? "");
    if (Number.isFinite(length) && length > SHARE_PHOTO_MAX_BYTES) {
      return null;
    }
    return sharePhotoFromBytes(new Uint8Array(await response.arrayBuffer()));
  } catch {
    return null;
  }
}
