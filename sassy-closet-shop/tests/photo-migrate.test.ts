import assert from "node:assert/strict";
import { describe, test } from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import {
  isExternalCoverUrl,
  migrateExternalCoversToBlob,
  type FetchImageFn,
  type ImageBlobPort,
} from "../lib/photo-migrate";
import type { CatalogDocument, Product } from "../lib/types";

function makeProduct(ma: string, srcs: string[]): Product {
  return {
    ma,
    type: "A",
    titleVn: `Test ${ma}`,
    titleEn: `Test ${ma}`,
    priceUsd: 30,
    qty: 1,
    status: "hold",
    colors: [],
    images: srcs.map((src, i) => ({ src, colorId: null, order: i })),
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "",
    fulfillment: "dropship",
    sourceLink: "",
  };
}

function makeDocument(products: Product[]): CatalogDocument {
  return {
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    products,
    settings: { announcementLines: [], facebookPageUrl: "" },
    updatedAt: new Date().toISOString(),
  };
}

function memoryImagePort(): ImageBlobPort & { puts: { pathname: string; url: string }[] } {
  const puts: { pathname: string; url: string }[] = [];
  return {
    puts,
    async putImage(pathname, _bytes, _contentType) {
      const url = `https://test-blob.public.blob.vercel-storage.com/${pathname}`;
      puts.push({ pathname, url });
      return { url };
    },
  };
}

const JPEG_BYTES = Buffer.from([0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46]);

describe("isExternalCoverUrl", () => {
  test("flags Catbox and Alicdn covers as external", () => {
    assert.equal(isExternalCoverUrl("https://files.catbox.moe/abc123.jpg"), true);
    assert.equal(isExternalCoverUrl("https://img.alicdn.com/imgextra/i1/123.jpg"), true);
  });

  test("Blob URLs are not external", () => {
    assert.equal(
      isExternalCoverUrl("https://abc.public.blob.vercel-storage.com/sassy-closet-shop/products/D05/x.jpg"),
      false,
    );
  });

  test("local paths and data URLs are not external", () => {
    assert.equal(isExternalCoverUrl("/products/D05/cover.jpg"), false);
    assert.equal(isExternalCoverUrl("/uploads/D05/abc.jpg"), false);
    assert.equal(isExternalCoverUrl("data:image/jpeg;base64,/9j/"), false);
    assert.equal(isExternalCoverUrl(""), false);
  });
});

describe("migrateExternalCoversToBlob", () => {
  test("rewrites Catbox/Alicdn covers to Blob, keeps local ones", async () => {
    const port = memoryImagePort();
    const fetchImage: FetchImageFn = async () => ({ bytes: JPEG_BYTES, contentType: "image/jpeg" });
    const doc = makeDocument([
      makeProduct("D05", ["https://files.catbox.moe/abc123.jpg", "/products/D05/cover.jpg"]),
      makeProduct("V03", ["https://img.alicdn.com/imgextra/i1/xyz.jpg"]),
    ]);

    const { document, report } = await migrateExternalCoversToBlob(doc, port, fetchImage);

    assert.equal(report.migrated.length, 2);
    assert.equal(report.errors.length, 0);
    assert.equal(port.puts.length, 2);
    // Pathnames land under the product's catalog image prefix.
    assert.ok(port.puts[0].pathname.startsWith("sassy-closet-shop/products/D05/migrated-"));
    assert.ok(port.puts[1].pathname.startsWith("sassy-closet-shop/products/V03/migrated-"));

    const d05 = document.products.find((p) => p.ma === "D05")!;
    assert.ok(d05.images[0].src.includes("blob.vercel-storage.com"));
    assert.equal(d05.images[1].src, "/products/D05/cover.jpg");
    const v03 = document.products.find((p) => p.ma === "V03")!;
    assert.ok(v03.images[0].src.includes("blob.vercel-storage.com"));

    // Never invents mã — same products in, same products out.
    assert.deepEqual(
      document.products.map((p) => p.ma).sort(),
      ["D05", "V03"],
    );
  });

  test("fetch failure keeps the original src — covers never go blank", async () => {
    const port = memoryImagePort();
    const fetchImage: FetchImageFn = async () => {
      throw new Error("ECONNREFUSED");
    };
    const doc = makeDocument([makeProduct("D05", ["https://files.catbox.moe/dead.jpg"])]);

    const { document, report } = await migrateExternalCoversToBlob(doc, port, fetchImage);

    assert.equal(report.migrated.length, 0);
    assert.equal(report.errors.length, 1);
    assert.equal(report.errors[0].ma, "D05");
    assert.equal(document.products[0].images[0].src, "https://files.catbox.moe/dead.jpg");
  });

  test("empty bytes are skipped, not uploaded", async () => {
    const port = memoryImagePort();
    const fetchImage: FetchImageFn = async () => ({ bytes: Buffer.alloc(0), contentType: "" });
    const doc = makeDocument([makeProduct("S05", ["https://example.com/empty.jpg"])]);

    const { document, report } = await migrateExternalCoversToBlob(doc, port, fetchImage);

    assert.equal(report.migrated.length, 0);
    assert.equal(report.skipped.length, 1);
    assert.equal(port.puts.length, 0);
    assert.equal(document.products[0].images[0].src, "https://example.com/empty.jpg");
  });

  test("no external covers — document unchanged", async () => {
    const port = memoryImagePort();
    let fetched = 0;
    const fetchImage: FetchImageFn = async () => {
      fetched += 1;
      return { bytes: JPEG_BYTES, contentType: "image/jpeg" };
    };
    const doc = makeDocument([makeProduct("A01", ["/products/A01/cover.jpg"])]);

    const { document, report } = await migrateExternalCoversToBlob(doc, port, fetchImage);

    assert.equal(fetched, 0);
    assert.equal(report.migrated.length, 0);
    assert.equal(document.products[0].images[0].src, "/products/A01/cover.jpg");
  });
});
