import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { isKnownSeedMa } from "../lib/catalog-contract";
import { getSeedDocument } from "../lib/catalog-store";
import {
  commitHubCatalog,
  hubIncomingFromSeed,
  prepareStoredHubCatalog,
} from "../scripts/apply-hub-live";
import type { CatalogDocument, Product } from "../lib/types";

function cloneDocument(document: CatalogDocument): CatalogDocument {
  return structuredClone(document);
}

function row(document: CatalogDocument, ma: string): Product {
  const product = document.products.find((item) => item.ma === ma);
  if (!product) {
    throw new Error(`missing ${ma}`);
  }
  return product;
}

function setRow(document: CatalogDocument, ma: string, patch: Partial<Product>): void {
  Object.assign(row(document, ma), patch);
}

test("seed file keeps P02 and P05 available at $25", () => {
  const raw = JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as {
    products: { ma: string; status: string; priceUsd: number | null }[];
  };
  for (const ma of ["P02", "P05"]) {
    const product = raw.products.find((item) => item.ma === ma);
    assert.equal(product?.status, "available", ma);
    assert.equal(product?.priceUsd, 25, ma);
  }
});

test("available hub price stays when the seed price is higher", () => {
  const seed = getSeedDocument();
  const incoming = hubIncomingFromSeed(seed);
  const seedA01 = row(incoming, "A01").priceUsd;
  assert.equal(typeof seedA01, "number");
  assert.ok((seedA01 as number) > 20);

  const stored = cloneDocument(seed);
  setRow(stored, "A01", { status: "available", priceUsd: 20 });
  const next = prepareStoredHubCatalog(stored, incoming);

  assert.equal(row(next, "A01").status, "available");
  assert.equal(row(next, "A01").priceUsd, 20);
});

test("available hub price stays when the seed price is lower", () => {
  const seed = getSeedDocument();
  const incoming = hubIncomingFromSeed(seed);
  const stored = cloneDocument(seed);
  setRow(stored, "A01", { status: "available", priceUsd: 40 });
  const next = prepareStoredHubCatalog(stored, incoming);

  assert.equal(row(next, "A01").status, "available");
  assert.equal(row(next, "A01").priceUsd, 40);
  assert.notEqual(row(next, "A01").priceUsd, row(incoming, "A01").priceUsd);
});

test("available P02 and P05 at $25 stay available at $25", () => {
  const seed = getSeedDocument();
  const incoming = hubIncomingFromSeed(seed);
  const stored = cloneDocument(seed);
  assert.equal(row(stored, "P02").status, "available");
  assert.equal(row(stored, "P02").priceUsd, 25);
  assert.equal(row(stored, "P05").status, "available");
  assert.equal(row(stored, "P05").priceUsd, 25);

  const next = prepareStoredHubCatalog(stored, incoming);
  assert.equal(row(next, "P02").status, "available");
  assert.equal(row(next, "P02").priceUsd, 25);
  assert.equal(row(next, "P05").status, "available");
  assert.equal(row(next, "P05").priceUsd, 25);
});

test("hold and sold hub rows do not take the seed available dollar", () => {
  const seed = getSeedDocument();
  const incoming = hubIncomingFromSeed(seed);
  const stored = cloneDocument(seed);
  setRow(stored, "P02", { status: "hold", priceUsd: null });
  setRow(stored, "P05", { status: "sold", priceUsd: null });

  const next = prepareStoredHubCatalog(stored, incoming);
  assert.equal(row(next, "P02").status, "hold");
  assert.equal(row(next, "P02").priceUsd, null);
  assert.equal(row(next, "P05").status, "sold");
  assert.equal(row(next, "P05").priceUsd, null);
  assert.equal(row(incoming, "P02").status, "available");
  assert.equal(row(incoming, "P02").priceUsd, 25);
  assert.equal(row(incoming, "P05").priceUsd, 25);
});

test("sold hub row keeps its stored dollar", () => {
  const seed = getSeedDocument();
  const incoming = hubIncomingFromSeed(seed);
  const stored = cloneDocument(seed);
  setRow(stored, "P05", { status: "sold", priceUsd: 25 });

  const next = prepareStoredHubCatalog(stored, incoming);
  assert.equal(row(next, "P05").status, "sold");
  assert.equal(row(next, "P05").priceUsd, 25);
  assert.equal(row(incoming, "P05").status, "available");
});

test("S06 at $25 and other extras stay out of the hub price copy", () => {
  const seed = getSeedDocument();
  const incoming = hubIncomingFromSeed(seed);
  const stored = cloneDocument(seed);
  const base = row(stored, "A01");
  stored.products.push({
    ...base,
    ma: "S06",
    type: "S",
    status: "available",
    priceUsd: 25,
    titleEn: "S06",
    titleVn: "S06",
  });
  stored.products.push({
    ...base,
    ma: "A04",
    type: "A",
    status: "hold",
    priceUsd: null,
    titleEn: "Extra",
    titleVn: "Extra",
  });

  const next = prepareStoredHubCatalog(stored, incoming);
  assert.equal(row(next, "S06").status, "available");
  assert.equal(row(next, "S06").priceUsd, 25);
  assert.equal(row(next, "A04").status, "hold");
  assert.equal(row(next, "A04").priceUsd, null);
  assert.equal(incoming.products.some((product) => product.ma === "S06" || product.ma === "A04"), false);
  assert.equal(isKnownSeedMa("S06"), false);
});

test("a rejected hub catalog is not written", async () => {
  const seed = getSeedDocument();
  const incoming = hubIncomingFromSeed(seed);
  const stored = cloneDocument(seed);
  setRow(stored, "A01", { status: "available", priceUsd: 20 });
  const prepared = prepareStoredHubCatalog(stored, incoming);
  const rejected = cloneDocument(prepared);
  setRow(rejected, "A01", { priceUsd: row(incoming, "A01").priceUsd });

  let writes = 0;
  await assert.rejects(
    () =>
      commitHubCatalog(rejected, stored, async () => {
        writes += 1;
        return "written";
      }),
    /A01 must keep its live price/,
  );
  assert.equal(writes, 0);
});

test("empty local path runs the failure checks before write", async () => {
  const incoming = hubIncomingFromSeed(getSeedDocument());
  const missingLink = cloneDocument(incoming);
  setRow(missingLink, "P02", { sourceLink: null });

  let writes = 0;
  await assert.rejects(
    () =>
      commitHubCatalog(missingLink, null, async () => {
        writes += 1;
        return "written";
      }),
    /recorded staff links \(P02\)/,
  );
  assert.equal(writes, 0);

  const short = cloneDocument(incoming);
  short.products = short.products.filter((product) => product.ma !== "H01");
  await assert.rejects(
    () =>
      commitHubCatalog(short, null, async () => {
        writes += 1;
        return "written";
      }),
    /Hub copy must keep 10 mãs, got 9/,
  );
  assert.equal(writes, 0);

  const written = await commitHubCatalog(incoming, null, async (document) => document);
  assert.equal(row(written, "P02").status, "available");
  assert.equal(row(written, "P02").priceUsd, 25);
  assert.equal(row(written, "P05").status, "available");
  assert.equal(row(written, "P05").priceUsd, 25);
});

test("clean available $25 catalog passes the pre-write check", async () => {
  const seed = getSeedDocument();
  const incoming = hubIncomingFromSeed(seed);
  const stored = cloneDocument(seed);
  const prepared = prepareStoredHubCatalog(stored, incoming);
  let writes = 0;
  const written = await commitHubCatalog(prepared, stored, async (document) => {
    writes += 1;
    return document;
  });
  assert.equal(writes, 1);
  assert.equal(row(written, "P02").status, "available");
  assert.equal(row(written, "P02").priceUsd, 25);
  assert.equal(row(written, "P05").priceUsd, 25);
});

test("hub script checks before write and does not require P02/P05 Hold", () => {
  const source = readFileSync(path.join(process.cwd(), "scripts", "apply-hub-live.ts"), "utf8");
  const mainBody = source.slice(source.indexOf("async function main"));
  const commitBody = source.slice(
    source.indexOf("export async function commitHubCatalog"),
    source.indexOf("async function main"),
  );
  assert.equal(source.includes("product.priceUsd < prior.priceUsd"), false);
  assert.equal(source.includes("must stay Hold"), false);
  assert.equal(source.includes("S06"), false);
  assert.equal(source.includes("ship"), false);
  assert.equal(mainBody.includes("writeLiveCatalogDocument("), false);
  assert.equal((mainBody.match(/commitHubCatalog/g) ?? []).length, 2);
  assert.ok(commitBody.indexOf("assertHubCopyReady") >= 0);
  assert.ok(commitBody.indexOf("return write(document)") > commitBody.indexOf("assertHubCopyReady"));
});
