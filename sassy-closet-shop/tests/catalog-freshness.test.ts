import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createMemoryBlobPort, writeCatalogToBlobPort } from "../lib/blob-catalog";
import { catalogBlobPath } from "../lib/catalog-contract";
import { catalogBodyMatches, catalogJsonMatches } from "../lib/catalog-roundtrip";
import { parseCatalogDocument, toCatalogDocumentJson } from "../lib/product-parse";

const PATHNAME = catalogBlobPath();

function loadFresh(): Record<string, unknown> {
  return JSON.parse(readFileSync(new URL("./fixtures/catalog-s06.json", import.meta.url), "utf8")) as Record<
    string,
    unknown
  >;
}

function withProductPrice(raw: Record<string, unknown>, ma: string, priceUsd: number): Record<string, unknown> {
  const products = raw.products;
  if (!Array.isArray(products)) {
    throw new Error("fixture needs products");
  }
  return {
    ...raw,
    products: products.map((item) => {
      if (typeof item !== "object" || item === null) return item;
      const row = item as Record<string, unknown>;
      if (row.ma !== ma) return item;
      return { ...row, priceUsd };
    }),
  };
}

test("a stale Blob updatedAt is still the same catalog body", async () => {
  const fresh = loadFresh();
  const freshJson = toCatalogDocumentJson(parseCatalogDocument(fresh));
  const stale = { ...fresh, updatedAt: "2020-01-01T00:00:00.000Z" };
  assert.equal(catalogJsonMatches(freshJson, stale), false);
  assert.equal(catalogBodyMatches(freshJson, stale), true);

  const port = createMemoryBlobPort();
  const staleRaw = JSON.parse(toCatalogDocumentJson(parseCatalogDocument(stale))) as unknown;
  port.getJson = async () => staleRaw;
  port.fetchJson = async () => staleRaw;
  const written = await writeCatalogToBlobPort(port, parseCatalogDocument(fresh), PATHNAME);
  const s06 = written.products.find((product) => product.ma === "S06");
  assert.equal(s06?.priceUsd, 25);
  assert.equal(written.updatedAt, "2026-10-15T00:00:00.000Z");
  assert.equal(written.products.some((product) => product.ma === "K06"), false);
});

test("an S06 dollar other than 25 is a different catalog body", () => {
  const fresh = loadFresh();
  const freshJson = toCatalogDocumentJson(parseCatalogDocument(fresh));
  const drifted = withProductPrice(fresh, "S06", 24);
  assert.equal(catalogBodyMatches(freshJson, drifted), false);
  assert.equal(catalogJsonMatches(freshJson, drifted), false);
  const parsed = parseCatalogDocument(fresh);
  assert.equal(parsed.products.find((product) => product.ma === "S06")?.priceUsd, 25);
});

test("a held mã on the Blob body is not the fresh catalog", () => {
  const fresh = loadFresh();
  const freshJson = toCatalogDocumentJson(parseCatalogDocument(fresh));
  const products = fresh.products;
  if (!Array.isArray(products)) {
    throw new Error("fixture needs products");
  }
  const s06 = products[0];
  if (typeof s06 !== "object" || s06 === null) {
    throw new Error("fixture needs S06");
  }
  const held = {
    ...(s06 as Record<string, unknown>),
    ma: "K06",
    type: "K",
    titleVn: "K06",
    titleEn: "K06",
    priceUsd: null,
    status: "hold",
  };
  const leaked = { ...fresh, products: [...products, held] };
  assert.equal(parseCatalogDocument(leaked).products.some((product) => product.ma === "K06"), true);
  assert.equal(catalogBodyMatches(freshJson, leaked), false);
});
