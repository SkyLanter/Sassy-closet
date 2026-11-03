import { readFileSync } from "node:fs";
import path from "node:path";
import {
  CATALOG_SCHEMA,
  KNOWN_SEED_MAS,
  catalogBlobPath,
  catalogExportFilename,
  catalogImagePrefix,
  catalogKvKey,
  isKnownSeedMa,
} from "../lib/catalog-contract";
import { assertBossPrices } from "../lib/boss-catalog";
import { getSeedDocument } from "../lib/catalog-store";
import { catalogFieldDiffs } from "../lib/catalog-roundtrip";
import {
  asCatalogDocument,
  assertCanonicalSerializedCatalog,
  parseCatalogDocument,
  toCatalogDocumentJson,
} from "../lib/product-parse";
import { siteId, siteMode } from "../lib/site-runtime";

function fail(message: string): never {
  throw new Error(message);
}

function assertNoShopHostname(rel: string): void {
  const text = readFileSync(path.join(process.cwd(), rel), "utf8");
  if (text.includes("sassy-closet-shop.vercel.app") || text.includes("sassy-closet.vercel.app")) {
    fail(`${rel} must not hardcode a shop hostname`);
  }
}

const seed = getSeedDocument();
if (seed.schema !== CATALOG_SCHEMA) {
  fail("Seed must declare catalog.v1");
}
if (seed.siteId !== siteId()) {
  fail(`Seed siteId ${seed.siteId} must match runtime ${siteId()}`);
}
if (siteMode() !== "test") {
  fail("Default SITE_MODE must be test in this repo");
}
if (catalogBlobPath() !== "sassy-closet-shop/catalog.v1.json") {
  fail(`Unexpected default blob path ${catalogBlobPath()}`);
}
if (catalogKvKey() !== "sassy-closet-shop:catalog.v1") {
  fail(`Unexpected default KV key ${catalogKvKey()}`);
}
if (catalogImagePrefix("A01") !== "sassy-closet-shop/products/A01") {
  fail("Image prefix must be SITE_ID/products/mã");
}
if (catalogBlobPath("sassy-closet-official") !== "sassy-closet-official/catalog.v1.json") {
  fail("Official SITE_ID must get its own Blob prefix");
}
if (catalogExportFilename() !== "sassy-closet-shop-catalog.v1.json") {
  fail("Export filename must include site id + catalog.v1");
}

const seedMas = seed.products.map((product) => product.ma);
if (seedMas.join(",") !== KNOWN_SEED_MAS.join(",")) {
  fail(`Seed mãs drifted: ${seedMas.join(",")}`);
}
for (const ma of seedMas) {
  if (!isKnownSeedMa(ma)) {
    fail(`Invented seed mã ${ma}`);
  }
}
assertBossPrices(seed.products);
for (const product of seed.products) {
  if (product.fulfillment !== "dropship") {
    fail(`Seed ${product.ma} must be dropship until Boss marks on_hand`);
  }
  if (product.sourceLink) {
    fail(`Seed ${product.ma} invented a Taobao sourceLink`);
  }
}

const json = toCatalogDocumentJson(seed);
assertCanonicalSerializedCatalog(json);
if (!json.includes(`"schema": "${CATALOG_SCHEMA}"`)) {
  fail("Serialized catalog missing schema");
}

const legacy = parseCatalogDocument(seed.products);
if (legacy.schema !== CATALOG_SCHEMA || legacy.products.length !== 10) {
  fail("Legacy array must upgrade to catalog.v1");
}

const stamped = asCatalogDocument(seed.products, seed.settings, "sassy-closet-official");
if (stamped.siteId !== "sassy-closet-official") {
  fail("Handoff stamp must rewrite siteId");
}

try {
  parseCatalogDocument({ schema: "catalog.v0", version: 1, products: seed.products, settings: seed.settings });
  fail("catalog.v0 must be rejected");
} catch (error) {
  if (!(error instanceof Error) || !error.message.includes("schema")) {
    fail("Wrong error for unsupported schema");
  }
}

assertNoShopHostname("lib/catalog-store.ts");
assertNoShopHostname("lib/blob-catalog.ts");
assertNoShopHostname("lib/catalog-contract.ts");
assertNoShopHostname("lib/site-runtime.ts");
assertNoShopHostname("lib/product-parse.ts");

const blobPort = readFileSync(path.join(process.cwd(), "lib/catalog-store.ts"), "utf8");
if (!blobPort.includes("cacheControlMaxAge: 0")) {
  fail("Blob catalog put must set cacheControlMaxAge: 0 or CDN keeps a stale catalog.v1");
}
if (!blobPort.includes("useCache: false") || !blobPort.includes("get(")) {
  fail("Blob catalog read must get() by pathname with useCache: false — list-only reads miss after Save");
}
if (blobPort.includes("next: { revalidate: 3600") || blobPort.includes("revalidate: 3600")) {
  fail("Do not wrap Blob catalog reads in fetch(..., { next: { revalidate: 3600 } })");
}

const refresh = readFileSync(path.join(process.cwd(), "lib/refresh-shop.ts"), "utf8");
if (!refresh.includes('revalidatePath("/m/[ma]", "page")') || !refresh.includes('revalidatePath("/c/[slug]", "page")')) {
  fail("refreshShop must revalidatePath /m/[ma] and /c/[slug] with page");
}
if (!refresh.includes("warmShopPaths")) {
  fail("refreshShop must warm public URLs after revalidatePath");
}

const adminOps = readFileSync(path.join(process.cwd(), "lib/admin-ops.ts"), "utf8");
if (!adminOps.includes("nextMaForLetter")) {
  fail("admin-ops must assign next mã (A03+) on Add");
}
if (adminOps.includes('nonAllowlistSaveError("A03")') || adminOps.includes("Add is closed")) {
  fail("admin-ops must not hard-lock Add A03");
}

if (blobPort.includes("store.json") && blobPort.includes("put(pathname")) {
  fail("Sell catalog must not write intake store.json");
}

const nextConfig = readFileSync(path.join(process.cwd(), "next.config.ts"), "utf8");
if (!nextConfig.includes('source: "/m/:path*"') || !nextConfig.includes("no-store")) {
  fail("Shop PDP routes must send no-store so /m/A01 cannot stay Vercel STALE after Save");
}

const coverRoute = readFileSync(path.join(process.cwd(), "app/products/[ma]/[file]/route.ts"), "utf8");
if (!coverRoute.includes("no-store") && !coverRoute.includes("NO_STORE")) {
  fail("Cover route must send no-store so /products/A01/cover.jpg cannot stay CDN HIT");
}
if (!coverRoute.includes("readPublicNamedFile") || coverRoute.includes("cover.svg")) {
  fail("Product image route must serve the requested public JPEG (photo-N), never an SVG placeholder");
}

const blobCatalog = readFileSync(path.join(process.cwd(), "lib/blob-catalog.ts"), "utf8");
if (!blobCatalog.includes("catalogJsonMatches") || !blobCatalog.includes("BLOB_READBACK_DELAYS_MS")) {
  fail("Blob put must retry canonical read-back (stale get() is not a failed Save)");
}
if (!blobCatalog.includes("catalogBodyMatches") || !blobCatalog.includes("roundTripMismatchError")) {
  fail("Blob put must ignore a stale updatedAt and name remaining field diffs");
}
if (!blobPort.includes("downloadUrl")) {
  fail("Blob put must read back downloadUrl as well as the public url");
}

const a01Edited = parseCatalogDocument({
  ...seed,
  products: seed.products.map((product) =>
    product.ma === "A01" ? { ...product, titleEn: "Kit prove top" } : product,
  ),
});
const titleDiffs = catalogFieldDiffs(a01Edited, seed);
if (!titleDiffs.some((line) => line.includes("products[A01].titleEn"))) {
  fail("Round-trip mismatch must name products[A01].titleEn");
}

console.log("catalog.v1 contract ok", {
  siteId: siteId(),
  blobPath: catalogBlobPath(),
  seedMas: seedMas.join(","),
});
