import assert from "node:assert/strict";
import test from "node:test";
import { readCatalogFromBlobPort, type BlobCatalogPort } from "../lib/blob-catalog";
import { isCatalogCorruptError } from "../lib/catalog-integrity";

const PATHNAME = "sassy-closet-shop/catalog.v1.json";

function port(overrides: Partial<BlobCatalogPort>): BlobCatalogPort {
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
    async getJson() {
      return null;
    },
    ...overrides,
  };
}

test("unreadable Blob JSON is corrupt and is not a missing catalog", async () => {
  let listed = false;
  await assert.rejects(
    readCatalogFromBlobPort(
      port({
        async getJson() {
          throw new SyntaxError("Unexpected token < in JSON at position 0");
        },
        async list() {
          listed = true;
          return [];
        },
      }),
      PATHNAME,
    ),
    (error: unknown) => {
      assert.equal(isCatalogCorruptError(error), true);
      assert.match(
        error instanceof Error ? error.message : "",
        /Blob catalog at sassy-closet-shop\/catalog\.v1\.json is corrupt and will not fall back to seed/,
      );
      return true;
    },
  );
  assert.equal(listed, false);
});

test("a listed Blob body that is not JSON is corrupt", async () => {
  await assert.rejects(
    readCatalogFromBlobPort(
      port({
        async getJson() {
          throw new Error("socket hang up");
        },
        async list() {
          return [{ pathname: PATHNAME, url: "https://blob.example/catalog.v1.json" }];
        },
        async fetchJson() {
          throw new SyntaxError("Unexpected end of JSON input");
        },
      }),
      PATHNAME,
    ),
    (error: unknown) => {
      assert.equal(isCatalogCorruptError(error), true);
      assert.match(
        error instanceof Error ? error.message : "",
        /will not fall back to seed/,
      );
      return true;
    },
  );
});

test("a missing Blob catalog stays missing so bootstrap can use seed", async () => {
  const document = await readCatalogFromBlobPort(
    port({
      async getJson() {
        return null;
      },
      async list() {
        return [];
      },
    }),
    PATHNAME,
  );
  assert.equal(document, null);
});

test("JSON that is not catalog.v1 stays a corrupt read", async () => {
  await assert.rejects(
    readCatalogFromBlobPort(
      port({
        async getJson() {
          return { nope: true };
        },
      }),
      PATHNAME,
    ),
    (error: unknown) => {
      assert.equal(isCatalogCorruptError(error), true);
      assert.match(
        error instanceof Error ? error.message : "",
        /will not fall back to seed/,
      );
      return true;
    },
  );
});
