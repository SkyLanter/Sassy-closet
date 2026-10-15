import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createMemoryBlobPort, readCatalogFromBlobPort, writeCatalogToBlobPort } from "../lib/blob-catalog";
import { catalogBlobPath } from "../lib/catalog-contract";
import { isCatalogCorruptError } from "../lib/catalog-integrity";
import { parseCatalogDocument } from "../lib/product-parse";

const PATHNAME = catalogBlobPath();

function corruptBody(): string {
  return readFileSync(new URL("./fixtures/corrupt-blob.txt", import.meta.url), "utf8");
}

function freshDocument() {
  const raw = JSON.parse(readFileSync(new URL("./fixtures/catalog-s06.json", import.meta.url), "utf8")) as unknown;
  return parseCatalogDocument(raw);
}

test("a corrupt Blob fixture is not a missing catalog and does not become seed", async () => {
  const port = createMemoryBlobPort();
  await port.put(PATHNAME, corruptBody());
  let seeded = false;
  await assert.rejects(
    readCatalogFromBlobPort(port, PATHNAME).then((document) => {
      if (document === null) seeded = true;
      return document;
    }),
    (error: unknown) => {
      assert.equal(isCatalogCorruptError(error), true);
      assert.match(
        error instanceof Error ? error.message : "",
        /Blob catalog at sassy-closet-shop\/catalog\.v1\.json is corrupt and will not fall back to seed/,
      );
      return true;
    },
  );
  assert.equal(seeded, false);
  const stored = port.store.get(PATHNAME);
  assert.equal(stored?.body.includes("S06"), false);
});

test("corrupt read-back after put does not return a catalog", async () => {
  const body = corruptBody();
  const port = createMemoryBlobPort();
  port.getJson = async () => JSON.parse(body) as unknown;
  port.fetchJson = async () => JSON.parse(body) as unknown;
  await assert.rejects(writeCatalogToBlobPort(port, freshDocument(), PATHNAME), (error: unknown) => {
    assert.equal(isCatalogCorruptError(error), true);
    assert.match(error instanceof Error ? error.message : "", /will not fall back to seed/);
    return true;
  });
});
