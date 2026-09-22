import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";
import { isValidMa, normalizeMa } from "@/lib/ma";
import { coverSrc } from "@/lib/product-media";
import { readLiveCatalogDocument } from "@/lib/catalog-store";
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

async function bytesFromCatalogSrc(
  src: string,
  ma: string,
): Promise<{ body: Buffer; type: string } | null> {
  const [base] = src.split("?");
  const embedded = base?.match(/^\/products\/([^/]+)\/([^/]+)$/);
  if (embedded) {
    const folder = normalizeMa(embedded[1] ?? ma);
    const file = embedded[2] ?? "";
    return (await readPublicNamedFile(folder, file)) ?? (await readPublicCover(folder)) ?? (await readPublicCover(ma));
  }
  if (isSelfCoverPath(src, ma)) {
    return readPublicCover(ma);
  }
  if (src.startsWith("/uploads/") || src.startsWith("/")) {
    try {
      const relative = src.split("?")[0] ?? src;
      const body = await readFile(path.join(process.cwd(), "public", relative.replace(/^\//, "")));
      return { body, type: mimeFor(relative) };
    } catch {
      return readPublicCover(ma);
    }
  }
  if (src.startsWith("http://") || src.startsWith("https://")) {
    try {
      const response = await fetch(src, {
        cache: "no-store",
        headers: { "Cache-Control": "no-cache" },
      });
      if (!response.ok) {
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
  if (!isValidMa(ma) || !isSellableMa(ma) || !FILE_RE.test(file)) {
    return new NextResponse("Not found", { status: 404, headers: NO_STORE_HEADERS });
  }

  const named = await readPublicNamedFile(ma, file);
  if (named) {
    return imageResponse(named);
  }

  const document = await readLiveCatalogDocument();
  const product = document.products.find((item) => item.ma === ma);
  if (!product) {
    return new NextResponse("Not found", { status: 404, headers: NO_STORE_HEADERS });
  }

  const wanted = product.images.find((image) => {
    const [base] = image.src.split("?");
    return Boolean(base?.endsWith(`/${file}`));
  });
  const target = wanted?.src ?? (file.toLowerCase().startsWith("cover") ? coverSrc(product) : undefined);
  let payload = target ? await bytesFromCatalogSrc(target, ma) : null;
  if (!payload && file.toLowerCase().startsWith("cover")) {
    payload = await readPublicCover(ma);
    if (!payload) {
      for (const image of product.images) {
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
