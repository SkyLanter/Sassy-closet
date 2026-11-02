import assert from "node:assert/strict";
import test from "node:test";
import { readCatalogFromBlobPort, type BlobCatalogPort } from "../lib/blob-catalog";
import { catalogBlobLegacyPaths, catalogBlobPath } from "../lib/catalog-contract";
import { isCatalogCorruptError } from "../lib/catalog-integrity";

const SHOP = "sassy-closet-shop";
const OFFICIAL = "sassy-closet-official";

type Stored = { kind: "json"; body: unknown } | { kind: "syntax" };

function row(ma: string, priceUsd: number): Record<string, unknown> {
  return { ma, qty: 1, status: "available", priceUsd, images: [] };
}

function port(files: Record<string, Stored>): BlobCatalogPort & { reads: string[] } {
  const reads: string[] = [];
  return {
    reads,
    async put() {
      return { url: "memory://blob" };
    },
    async list() {
      return [];
    },
    async fetchJson() {
      throw new Error("legacy fallback reads by pathname");
    },
    async getJson(pathname) {
      reads.push(pathname);
      const stored = files[pathname];
      if (!stored) return null;
      if (stored.kind === "syntax") {
        throw new SyntaxError(`Unexpected token in ${pathname}`);
      }
      return stored.body;
    },
  };
}

async function withSite<T>(id: string, run: () => Promise<T>): Promise<T> {
  const prevSite = process.env.SITE_ID;
  const prevPublic = process.env.NEXT_PUBLIC_SITE_ID;
  process.env.SITE_ID = id;
  delete process.env.NEXT_PUBLIC_SITE_ID;
  try {
    return await run();
  } finally {
    if (prevSite === undefined) delete process.env.SITE_ID;
    else process.env.SITE_ID = prevSite;
    if (prevPublic === undefined) delete process.env.NEXT_PUBLIC_SITE_ID;
    else process.env.NEXT_PUBLIC_SITE_ID = prevPublic;
  }
}

test("legacy blob keys stay the pre-v1 catalog.json paths", () => {
  assert.deepEqual(catalogBlobLegacyPaths(SHOP), [`${SHOP}/catalog.json`]);
  assert.deepEqual(catalogBlobLegacyPaths(OFFICIAL), [
    `${OFFICIAL}/catalog.json`,
    `${SHOP}/catalog.json`,
  ]);
  assert.equal(catalogBlobPath(SHOP), `${SHOP}/catalog.v1.json`);
  assert.equal(catalogBlobPath(OFFICIAL), `${OFFICIAL}/catalog.v1.json`);
});

test("a missing catalog.v1.json is read from that site's catalog.json", async () => {
  await withSite(SHOP, async () => {
    const current = catalogBlobPath();
    const legacy = `${SHOP}/catalog.json`;
    const blob = port({
      [legacy]: { kind: "json", body: [row("A01", 27)] },
    });
    const document = await readCatalogFromBlobPort(blob);
    assert.equal(document?.products[0]?.ma, "A01");
    assert.equal(document?.products[0]?.priceUsd, 27);
    assert.deepEqual(blob.reads, [current, legacy]);
  });
});

test("catalog.v1.json wins and a different legacy file is not read", async () => {
  await withSite(SHOP, async () => {
    const current = catalogBlobPath();
    const legacy = `${SHOP}/catalog.json`;
    const blob = port({
      [current]: { kind: "json", body: [row("A01", 27)] },
      [legacy]: { kind: "json", body: [row("A01", 99)] },
    });
    const document = await readCatalogFromBlobPort(blob, current);
    assert.equal(document?.products[0]?.priceUsd, 27);
    assert.deepEqual(blob.reads, [current]);
  });
});

test("corrupt catalog.v1.json does not fall through to a good legacy catalog", async () => {
  await withSite(SHOP, async () => {
    const current = catalogBlobPath();
    const legacy = `${SHOP}/catalog.json`;
    const blob = port({
      [current]: { kind: "syntax" },
      [legacy]: { kind: "json", body: [row("Q02", 30)] },
    });
    await assert.rejects(readCatalogFromBlobPort(blob, current), (error: unknown) => {
      assert.equal(isCatalogCorruptError(error), true);
      assert.match(error instanceof Error ? error.message : "", /will not fall back to seed/);
      assert.match(error instanceof Error ? error.message : "", /catalog\.v1\.json/);
      return true;
    });
    assert.deepEqual(blob.reads, [current]);
  });
});

test("catalog.v1.json that is not a catalog does not fall through to legacy", async () => {
  await withSite(SHOP, async () => {
    const current = catalogBlobPath();
    const legacy = `${SHOP}/catalog.json`;
    const blob = port({
      [current]: { kind: "json", body: { nope: true } },
      [legacy]: { kind: "json", body: [row("Q02", 30)] },
    });
    await assert.rejects(readCatalogFromBlobPort(blob, current), (error: unknown) => {
      assert.equal(isCatalogCorruptError(error), true);
      assert.match(error instanceof Error ? error.message : "", /will not fall back to seed/);
      return true;
    });
    assert.deepEqual(blob.reads, [current]);
  });
});

test("another site reads its own catalog.json before the shared shop key", async () => {
  await withSite(OFFICIAL, async () => {
    const current = catalogBlobPath();
    const ownLegacy = `${OFFICIAL}/catalog.json`;
    const shared = `${SHOP}/catalog.json`;
    const blob = port({
      [ownLegacy]: { kind: "json", body: [row("A01", 30)] },
      [shared]: { kind: "json", body: [row("A01", 21)] },
    });
    const document = await readCatalogFromBlobPort(blob);
    assert.equal(document?.products[0]?.priceUsd, 30);
    assert.deepEqual(blob.reads, [current, ownLegacy]);
  });
});

test("another site falls back to the shared shop catalog.json when its own keys are missing", async () => {
  await withSite(OFFICIAL, async () => {
    const current = catalogBlobPath();
    const ownLegacy = `${OFFICIAL}/catalog.json`;
    const shared = `${SHOP}/catalog.json`;
    const blob = port({
      [shared]: { kind: "json", body: [row("A01", 21)] },
    });
    const document = await readCatalogFromBlobPort(blob);
    assert.equal(document?.products[0]?.ma, "A01");
    assert.equal(document?.products[0]?.priceUsd, 21);
    assert.deepEqual(blob.reads, [current, ownLegacy, shared]);
  });
});

test("a corrupt catalog.v1.json on another site does not use the shared shop catalog", async () => {
  await withSite(OFFICIAL, async () => {
    const current = catalogBlobPath();
    const shared = `${SHOP}/catalog.json`;
    const blob = port({
      [current]: { kind: "syntax" },
      [shared]: { kind: "json", body: [row("A01", 21)] },
    });
    await assert.rejects(readCatalogFromBlobPort(blob), (error: unknown) => {
      assert.equal(isCatalogCorruptError(error), true);
      return true;
    });
    assert.deepEqual(blob.reads, [current]);
  });
});
