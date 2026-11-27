import assert from "node:assert/strict";
import { test } from "node:test";
import { saveShopCatalogProduct, type ShopCatalogPort } from "../lib/shop-catalog";

/**
 * Two shop-desk saves that overlap must both land. The catalog file is one
 * document, so a save that read the file before the other write finishes
 * would put the older document back and drop the other mã's edit.
 */
test("two overlapping shop catalog saves both keep their titles and leave S06 at $25", async () => {
  const port = gatingCatalogPort(catalogWithS06());
  const allow = async () => ({ ok: true as const });
  const first = saveShopCatalogProduct(
    port,
    { ma: "A01", titleVn: "Áo một — giữ" },
    { now: "2026-11-27T00:00:00.000Z", revalidate: allow },
  );
  await port.firstWriteStarted;
  const second = saveShopCatalogProduct(
    port,
    { ma: "A03", titleVn: "Áo hai — giữ" },
    { now: "2026-11-27T00:00:01.000Z", revalidate: allow },
  );
  await new Promise((resolve) => setTimeout(resolve, 30));
  port.releaseFirstWrite();
  const [savedFirst, savedSecond] = await Promise.all([first, second]);
  assert.equal(savedFirst.ok, true);
  assert.equal(savedSecond.ok, true);

  const products = productsByMa(port.snapshot());
  assert.equal(products.A01?.titleVn, "Áo một — giữ");
  assert.equal(products.A03?.titleVn, "Áo hai — giữ");
  assert.equal(products.S06?.status, "available");
  assert.equal(products.S06?.priceUsd, 25);
  assert.equal(products.A01?.priceUsd, 20);
  assert.equal(products.A03?.priceUsd, 12);
});

type ProductSnap = {
  ma: string;
  titleVn?: string;
  status?: string;
  priceUsd?: number | null;
};

function productsByMa(snapshot: string): Record<string, ProductSnap> {
  const parsed = JSON.parse(snapshot) as { products: ProductSnap[] };
  return Object.fromEntries(parsed.products.map((product) => [product.ma, product]));
}

function catalogWithS06(): Record<string, unknown> {
  return {
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    updatedAt: "2026-11-01T00:00:00.000Z",
    products: [
      {
        ma: "A01",
        titleVn: "Áo cũ",
        titleEn: "Old top",
        descriptionVn: "",
        descriptionEn: "",
        priceUsd: 20,
        status: "available",
        colors: [{ id: "ca0100", name: "Vàng" }],
      },
      {
        ma: "A03",
        titleVn: "Áo khác",
        titleEn: "Other top",
        descriptionVn: "",
        descriptionEn: "",
        priceUsd: 12,
        status: "available",
        colors: [{ id: "ca0300", name: "Đen" }],
      },
      {
        ma: "S06",
        titleVn: "Set",
        titleEn: "Set",
        descriptionVn: "",
        descriptionEn: "",
        priceUsd: 25,
        status: "available",
        colors: [{ id: "cs0600", name: "Trắng" }],
      },
    ],
  };
}

/**
 * The first write pauses until the test releases it, so a second save can
 * read the same document if the writer does not wait its turn.
 */
function gatingCatalogPort(initial: unknown): ShopCatalogPort & {
  snapshot: () => string;
  firstWriteStarted: Promise<void>;
  releaseFirstWrite: () => void;
} {
  let body = `${JSON.stringify(initial, null, 2)}\n`;
  let writes = 0;
  let markStarted: () => void = () => {};
  const firstWriteStarted = new Promise<void>((resolve) => {
    markStarted = resolve;
  });
  let release: () => void = () => {};
  const released = new Promise<void>((resolve) => {
    release = resolve;
  });
  return {
    snapshot() {
      return body;
    },
    firstWriteStarted,
    releaseFirstWrite() {
      release();
    },
    async read() {
      return JSON.parse(body) as unknown;
    },
    async write(next) {
      writes += 1;
      if (writes === 1) {
        markStarted();
        await released;
      }
      body = next;
      return { url: "memory://sassy-closet-shop/catalog.v1.json" };
    },
  };
}
