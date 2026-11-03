import assert from "node:assert/strict";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { test } from "node:test";
import { GET } from "../app/api/shop-catalog/route";
import {
  memoryShopCatalogPort,
  saveShopCatalogProduct,
  type ShopCatalogPort,
} from "../lib/shop-catalog";
import { loadShopCatalogForAdmin } from "../lib/shop-catalog-store";

const ENV_KEYS = ["SHOP_BLOB_READ_WRITE_TOKEN", "BLOB_READ_WRITE_TOKEN", "VERCEL", "SHOP_CATALOG_FILE"] as const;

const SECRET_READ_ERROR = "Failed to fetch https://blob.example/secret-token";
const SAFE_READ_ERROR = "Shop catalog could not be read.";
const MISSING_ERROR = "Shop catalog is missing.";

function sampleCatalog(): Record<string, unknown> {
  return {
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    allowlist: ["A01"],
    settings: { announcementLines: ["keep"], facebookPageUrl: "https://example.com/page" },
    products: [
      {
        ma: "A01",
        type: "A",
        titleVn: "Áo len puppy",
        titleEn: "Puppy cardigan",
        priceUsd: 20,
        qty: 1,
        status: "available",
        colors: [{ id: "ca0100", hex: "#F5D76E", name: "Yellow", note: "" }],
        images: [{ src: "/products/A01/cover.jpg", colorId: "ca0100", order: 1 }],
        sizes: ["S", "M"],
        sourceLink: "https://e.tb.cn/example",
        extra: "keep-me",
      },
      {
        ma: "S06",
        type: "S",
        titleVn: "Set",
        titleEn: "Set",
        priceUsd: 25,
        qty: 1,
        status: "available",
        colors: [{ id: "cs0600", hex: "#ffffff", name: "White", note: "" }],
        images: [],
        sizes: ["S"],
      },
    ],
  };
}

function catalogPrice(snapshot: string | null, ma: string): number | null | undefined {
  const parsed = JSON.parse(snapshot ?? "{}") as {
    products: { ma: string; priceUsd: number | null }[];
  };
  return parsed.products.find((product) => product.ma === ma)?.priceUsd;
}

function restoreEnv(previous: Partial<Record<(typeof ENV_KEYS)[number], string | undefined>>) {
  for (const key of ENV_KEYS) {
    const value = previous[key];
    if (value === undefined) {
      delete process.env[key];
    } else {
      process.env[key] = value;
    }
  }
}

async function withCorruptCatalogFile(run: (file: string) => Promise<void>): Promise<void> {
  const previous: Partial<Record<(typeof ENV_KEYS)[number], string | undefined>> = {};
  for (const key of ENV_KEYS) {
    previous[key] = process.env[key];
  }
  delete process.env.SHOP_BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_READ_WRITE_TOKEN;
  delete process.env.VERCEL;
  const dir = mkdtempSync(path.join(tmpdir(), "shop-catalog-read-down-"));
  const file = path.join(dir, "catalog.v1.json");
  writeFileSync(file, "not-json");
  process.env.SHOP_CATALOG_FILE = file;
  try {
    await run(file);
  } finally {
    restoreEnv(previous);
    rmSync(dir, { recursive: true, force: true });
  }
}

test("save returns 503 when catalog read throws and does not write", async () => {
  let writes = 0;
  const port: ShopCatalogPort = {
    async read() {
      throw new Error(SECRET_READ_ERROR);
    },
    async write() {
      writes += 1;
      return { url: "memory://sassy-closet-shop/catalog.v1.json" };
    },
  };
  const logged: string[] = [];
  const original = console.error;
  console.error = (...args: unknown[]) => {
    logged.push(args.map((arg) => String(arg)).join(" "));
  };
  try {
    const result = await saveShopCatalogProduct(port, { ma: "A01", priceUsd: 27 });
    assert.equal(result.ok, false);
    if (!result.ok) {
      assert.equal(result.status, 503);
      assert.equal(result.blobWritten, false);
      assert.equal(result.error, SAFE_READ_ERROR);
      const encoded = JSON.stringify(result);
      assert.equal(encoded.includes("blob.example"), false);
      assert.equal(encoded.includes("secret-token"), false);
      assert.equal(result.error.includes("blob.example"), false);
      assert.equal(result.error.includes("secret-token"), false);
    }
    assert.equal(writes, 0);
    const logs = logged.join("\n");
    assert.equal(logs.includes("blob.example"), false);
    assert.equal(logs.includes("secret-token"), false);
  } finally {
    console.error = original;
  }
});

test("save returns 404 when the catalog read misses and does not write", async () => {
  let writes = 0;
  const port: ShopCatalogPort = {
    async read() {
      return null;
    },
    async write() {
      writes += 1;
      return { url: "memory://sassy-closet-shop/catalog.v1.json" };
    },
  };
  const result = await saveShopCatalogProduct(port, { ma: "A01", priceUsd: 27 });
  assert.equal(result.ok, false);
  if (!result.ok) {
    assert.equal(result.status, 404);
    assert.equal(result.error, MISSING_ERROR);
    assert.equal(result.blobWritten, false);
  }
  assert.equal(writes, 0);
});

test("admin load turns a corrupt catalog file into the safe alert error", async () => {
  await withCorruptCatalogFile(async (file) => {
    const loaded = await loadShopCatalogForAdmin();
    assert.equal(loaded.ok, false);
    if (!loaded.ok) {
      assert.equal(loaded.error, SAFE_READ_ERROR);
      assert.equal("status" in loaded, false);
      assert.equal(loaded.error.includes(file), false);
      assert.equal(loaded.error.includes("Unexpected token"), false);
    }
  });
});

test("GET /api/shop-catalog returns 503 JSON when the catalog file is not JSON", async () => {
  await withCorruptCatalogFile(async (file) => {
    const response = await GET();
    assert.equal(response.status, 503);
    assert.match(response.headers.get("x-robots-tag") ?? "", /noindex/i);
    const raw = await response.text();
    const body = JSON.parse(raw) as { ok?: boolean; error?: string };
    assert.equal(body.ok, false);
    assert.equal(body.error, SAFE_READ_ERROR);
    assert.equal(raw.includes(file), false);
    assert.equal(raw.includes("Unexpected token"), false);
  });
});

test("memory port still saves a non-S06 price and refuses an S06 price of 30", async () => {
  const port = memoryShopCatalogPort(sampleCatalog());
  const saved = await saveShopCatalogProduct(
    port,
    { ma: "A01", priceUsd: 27 },
    { revalidate: async () => ({ ok: true }) },
  );
  assert.equal(saved.ok, true);
  if (saved.ok) {
    assert.equal(saved.status, 200);
    assert.equal(saved.blobWritten, true);
  }
  assert.equal(catalogPrice(port.snapshot(), "A01"), 27);
  assert.equal(catalogPrice(port.snapshot(), "S06"), 25);

  const locked = memoryShopCatalogPort(sampleCatalog());
  const before = locked.snapshot();
  const refused = await saveShopCatalogProduct(
    locked,
    { ma: "S06", priceUsd: 30 },
    { revalidate: async () => ({ ok: true }) },
  );
  assert.equal(refused.ok, false);
  if (!refused.ok) {
    assert.equal(refused.status, 400);
    assert.equal(refused.blobWritten, false);
    assert.equal(refused.error, "S06 stays available at $25.");
  }
  assert.equal(locked.snapshot(), before);
  assert.equal(catalogPrice(locked.snapshot(), "S06"), 25);
  assert.equal(catalogPrice(locked.snapshot(), "A01"), 20);
});
