import assert from "node:assert/strict";
import test from "node:test";
import { readCatalogFromBlobPort, type BlobCatalogPort } from "../lib/blob-catalog";
import { catalogBlobLegacyPaths } from "../lib/catalog-contract";
import { isCatalogCorruptError } from "../lib/catalog-integrity";

const CURRENT = "sassy-closet-shop/catalog.v1.json";
const LEGACY = catalogBlobLegacyPaths()[0];

const emptyCurrent = {
  schema: "catalog.v1",
  version: 1,
  products: [],
};

const legacyCatalog = {
  schema: "catalog.v1",
  version: 1,
  products: [
    {
      ma: "A01",
      type: "A",
      titleVn: "Ao",
      titleEn: "Top",
      priceUsd: 26,
      qty: 1,
      status: "available",
      colors: [],
      images: [],
      sizes: [],
      fulfillment: "dropship",
      sourceLink: null,
    },
  ],
};

function port(reads: string[]): BlobCatalogPort {
  return {
    async put() {
      return { url: "memory://blob/catalog.v1.json" };
    },
    async list() {
      return [];
    },
    async fetchJson() {
      return null;
    },
    async getJson(pathname: string) {
      reads.push(pathname);
      if (pathname === CURRENT) {
        return emptyCurrent;
      }
      if (pathname === LEGACY) {
        return legacyCatalog;
      }
      return null;
    },
  };
}

test("an empty products array is corrupt and does not open the older catalog file", async () => {
  assert.equal(LEGACY, "sassy-closet-shop/catalog.json");
  const reads: string[] = [];
  await assert.rejects(
    readCatalogFromBlobPort(port(reads), CURRENT),
    (error: unknown) => {
      assert.equal(isCatalogCorruptError(error), true);
      const message = error instanceof Error ? error.message : "";
      assert.match(message, /will not fall back to seed/);
      assert.match(message, /cannot be empty/);
      return true;
    },
  );
  assert.deepEqual(reads, [CURRENT]);
});
