import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";
import { catalogImageSrcBlocked } from "@/lib/catalog-image-src";
import { readLiveCatalogDocumentForShop } from "@/lib/catalog-store";
import { isOffLiveSell } from "@/lib/held-incomplete";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";
import { isValidMa, normalizeMa } from "@/lib/ma";
import { coverSrc } from "@/lib/product-media";
import { isSellableMa } from "@/lib/sell-contract";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const FILE_RE = /^(cover(?:-[a-f0-9]{8,})?|photo-\d+)\.(jpe?g|png|webp)$/i;

function mimeFor(fileName: string): string {
  const ext = path.extname(fileName).toLowerCase();
  switch (ext) {
    case ".jpg":
    case ".jpeg":
      return "image/jpeg";
    case ".png":
      return "image/png";
    case ".webp":
      return "image/webp";
    default:
      return "application/octet-stream";
  }
}

function publicProductPath(ma: string, file: string): string | null {
  if (path.basename(file) !== file || file.includes("..") || file.includes("/") || file.includes("\\")) {
    return null;
  }
  return path.join(process.cwd(), "public", "products", ma, file);
}

async function readPublicNamedFile(ma: string, file: string): Promise<{ body: Buffer; type: string } | null> {
  const dest = publicProductPath(ma, file);
  if (!dest) {
    return null;
  }
  try {
    const body = await readFile(dest);
    return { body, type: mimeFor(file) };
  } catch {
    return null;
  }
}

async function readPublicCover(ma: string): Promise<{ body: Buffer; type: string } | null> {
  const names = ["cover.jpg", "cover.jpeg", "cover.png", "cover.webp"];
  for (const name of names) {
    const payload = await readPublicNamedFile(ma, name);
    if (payload) {
      return payload;
    }
  }
  return null;
}

function isSelfCoverPath(src: string, ma: string): boolean {
  const [base] = src.split("?");
  return Boolean(base && /^\/products\/[^/]+\/cover\./i.test(base) && base.includes(`/${ma}/`));
}

/** Local catalog src, confined to public/, after `..` is resolved. */
function publicFileForSrc(src: string): string | null {
  const relative = (src.split("#")[0]?.split("?")[0] ?? src).replace(/^\/+/, "");
  if (!relative || relative.includes("\0")) {
    return null;
  }
  const publicRoot = path.resolve(process.cwd(), "public");
  const absolute = path.resolve(publicRoot, relative);
  const rootWithSep = publicRoot.endsWith(path.sep) ? publicRoot : `${publicRoot}${path.sep}`;
  if (!absolute.startsWith(rootWithSep)) {
    return null;
  }
  const normalized = `/${path.relative(publicRoot, absolute).split(path.sep).join("/")}`;
  if (catalogImageSrcBlocked(normalized)) {
    return null;
  }
  return absolute;
}

const CATALOG_FETCH_HEADERS = { "Cache-Control": "no-cache" } as const;

/** Follow a few redirects, and stop before a hop lands on a held folder. */
async function fetchCatalogUrl(src: string): Promise<Response | null> {
  let current = src;
  for (let hop = 0; hop < 4; hop += 1) {
    if (catalogImageSrcBlocked(current)) {
      return null;
    }
    const response = await fetch(current, {
      cache: "no-store",
      redirect: "manual",
      headers: CATALOG_FETCH_HEADERS,
    });
    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get("location");
      await response.body?.cancel();
      if (!location) {
        return null;
      }
      current = new URL(location, current).toString();
      continue;
    }
    return response;
  }
  return null;
}

async function bytesFromCatalogSrc(
  src: string,
  ma: string,
): Promise<{ body: Buffer; type: string } | null> {
  // A live mã's cover URL must not fetch or read a held folder, including Blob URLs.
  if (catalogImageSrcBlocked(src)) {
    return null;
  }
  const [base] = src.split("?");
  const embedded = base?.match(/^\/products\/([^/]+)\/([^/]+)$/);
  if (embedded) {
    const folder = normalizeMa(embedded[1] ?? ma);
    const file = embedded[2] ?? "";
    if (isOffLiveSell(folder)) {
      return null;
    }
    return (await readPublicNamedFile(folder, file)) ?? (await readPublicCover(folder)) ?? (await readPublicCover(ma));
  }
  if (isSelfCoverPath(src, ma)) {
    return readPublicCover(ma);
  }
  if (src.startsWith("/uploads/") || src.startsWith("/")) {
    const dest = publicFileForSrc(src);
    if (!dest) {
      return readPublicCover(ma);
    }
    try {
      const body = await readFile(dest);
      return { body, type: mimeFor(dest) };
    } catch {
      return readPublicCover(ma);
    }
  }
  if (src.startsWith("http://") || src.startsWith("https://")) {
    try {
      const response = await fetchCatalogUrl(src);
      if (!response || !response.ok) {
        return readPublicCover(ma);
      }
      const body = Buffer.from(await response.arrayBuffer());
      const type = response.headers.get("content-type") || "image/jpeg";
      return { body, type };
    } catch {
      return readPublicCover(ma);
    }
  }
  return readPublicCover(ma);
}

function imageResponse(payload: { body: Buffer; type: string }): NextResponse {
  return new NextResponse(new Uint8Array(payload.body), {
    status: 200,
    headers: {
      ...NO_STORE_HEADERS,
      "Content-Type": payload.type,
    },
  });
}

export async function GET(
  _request: Request,
  context: { params: Promise<{ ma: string; file: string }> },
) {
  const { ma: rawMa, file } = await context.params;
  const ma = normalizeMa(rawMa);
  if (!isValidMa(ma) || !isSellableMa(ma) || isOffLiveSell(ma) || !FILE_RE.test(file)) {
    return new NextResponse("Not found", { status: 404, headers: NO_STORE_HEADERS });
  }

  const named = await readPublicNamedFile(ma, file);
  if (named) {
    return imageResponse(named);
  }

  const document = await readLiveCatalogDocumentForShop();
  const product = document.products.find((item) => item.ma === ma);
  if (!product) {
    return new NextResponse("Not found", { status: 404, headers: NO_STORE_HEADERS });
  }

  const wanted = product.images.find((image) => {
    if (catalogImageSrcBlocked(image.src)) {
      return false;
    }
    const [base] = image.src.split("?");
    return Boolean(base?.endsWith(`/${file}`));
  });
  const cover = file.toLowerCase().startsWith("cover") ? coverSrc(product) : undefined;
  const target = wanted?.src ?? (cover && !catalogImageSrcBlocked(cover) ? cover : undefined);
  let payload = target ? await bytesFromCatalogSrc(target, ma) : null;
  if (!payload && file.toLowerCase().startsWith("cover")) {
    payload = await readPublicCover(ma);
    if (!payload) {
      for (const image of product.images) {
        if (catalogImageSrcBlocked(image.src)) {
          continue;
        }
        payload = await bytesFromCatalogSrc(image.src, ma);
        if (payload) {
          break;
        }
      }
    }
  }
  if (!payload) {
    return new NextResponse("Not found", { status: 404, headers: NO_STORE_HEADERS });
  }

  return imageResponse(payload);
}
