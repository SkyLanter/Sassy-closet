import { readFileSync } from "node:fs";
import path from "node:path";
import {
  addProductToCatalog,
  bulkHoldInCatalog,
  removeProductFromCatalog,
  renameProductInCatalog,
  saveProductInCatalog,
} from "../lib/admin-ops";
import { nextMaForLetter } from "../lib/ma";
import { assertCanonicalSerializedCatalog, parseCatalogDocument, toCatalogDocumentJson } from "../lib/product-parse";
import {
  assertLiveCatalogIntegrity,
  inspectCatalogIntegrity,
  looksLikeOfficialMa,
} from "../lib/catalog-integrity";
import { parseProduct } from "../lib/product-parse";
import {
  isRecoverableSaveTransportError,
  liveProductReflectsFields,
  parseAdminJsonResponse,
} from "../lib/admin-client-save";
import { isCompleteSaveReceipt, silentSaveError } from "../lib/save-receipt";
import { isOpaqueRscError, opaquePostSaveMessage } from "../lib/opaque-rsc-error";
import { assertImportSellContract, NON_ALLOWLIST_SAVE_ERROR } from "../lib/sell-contract";
import { bossRow } from "../lib/boss-catalog";
import { shopVisibleProducts } from "../lib/site-settings";
import type { Product } from "../lib/types";

function holdFields() {
  return {
    titleEn: "Sell-test top",
    titleVn: "Áo test",
    descriptionEn: "One unique top for sell-test.",
    descriptionVn: "Áo độc bản — test.",
    status: "hold" as const,
    priceUsd: null,
    colors: [] as Product["colors"],
    images: [] as Product["images"],
  };
}

function fail(message: string): never {
  throw new Error(message);
}

const seedPath = path.join(process.cwd(), "data", "products.json");
const seedDocument = parseCatalogDocument(JSON.parse(readFileSync(seedPath, "utf8")) as unknown);
assertCanonicalSerializedCatalog(toCatalogDocumentJson(seedDocument));
const seed = seedDocument.products;
const mas = seed.map((product) => product.ma);

// The seed catalog grows (A01–A15 now) — derive the next mã from the seed
// instead of hardcoding A03, so this smoke stays green as Boss adds mãs.
const nextA = nextMaForLetter("A", mas);

const added = addProductToCatalog(seed, "A", holdFields());
if (!added.ok) {
  fail(`Add ${nextA} must Save, got ${added.error}`);
}
if (added.ma !== nextA) {
  fail(`Add letter A must assign ${nextA}, got ${added.ma}`);
}
if (!added.products.some((product) => product.ma === nextA)) {
  fail(`Add must insert ${nextA} into the catalog`);
}
if (!shopVisibleProducts(added.products).some((product) => product.ma === nextA)) {
  fail(`${nextA} must appear on the shop after Add (hold | available)`);
}

const savedNextA = saveProductInCatalog(added.products, nextA, {
  ...holdFields(),
  titleEn: `Top — ${nextA} saved`,
});
if (!savedNextA.ok) {
  fail(`Save ${nextA} after Add must work, got ${savedNextA.error}`);
}
if (savedNextA.products.find((product) => product.ma === nextA)?.titleEn !== `Top — ${nextA} saved`) {
  fail(`${nextA} title did not save`);
}

const a01Price = bossRow("A01")?.priceUsd;
if (a01Price == null) {
  fail("Boss list must carry an A01 price");
}

const titled = saveProductInCatalog(seed, "A01", {
  titleEn: "Top — edited",
  titleVn: "Áo",
  descriptionEn: "One unique top. Message A01 for real photos and size.",
  descriptionVn: "Áo độc bản — một chiếc.",
  status: "available",
  priceUsd: a01Price,
  colors: [],
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
});
if (!titled.ok) {
  fail(titled.error);
}
if (titled.products.find((product) => product.ma === "A01")?.titleEn !== "Top — edited") {
  fail("A01 title did not save");
}

const warehouseLie = saveProductInCatalog(seed, "A01", {
  titleEn: "Top",
  titleVn: "Áo",
  descriptionEn: "One unique top on hand. Message A01.",
  descriptionVn: "Áo độc bản — một chiếc đang có.",
  status: "available",
  priceUsd: a01Price,
  colors: [],
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
});
if (warehouseLie.ok) {
  fail("Save A01 must reject warehouse on-hand / đang có copy");
}
if (!warehouseLie.ok && !/on hand|đang có/.test(warehouseLie.error)) {
  fail(`Warehouse reject must name the lie, got ${warehouseLie.error}`);
}

const namedNoPhoto = saveProductInCatalog(titled.products, "A01", {
  titleEn: "Top — edited",
  titleVn: "Áo",
  descriptionEn: "One unique top. Message A01 for real photos and size.",
  descriptionVn: "Áo độc bản — một chiếc.",
  status: "available",
  priceUsd: a01Price,
  colors: [{ id: "cblackcolor01", hex: "#111111", name: "Black", note: "Hoa" }],
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
});
if (!namedNoPhoto.ok) {
  fail(`Named color without a tagged photo must Save, got ${namedNoPhoto.error}`);
}

const usSize = saveProductInCatalog(titled.products, "A01", {
  titleEn: "Top — edited",
  titleVn: "Áo",
  descriptionEn: "desc",
  descriptionVn: "desc",
  status: "available",
  priceUsd: a01Price,
  colors: [],
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
  sizes: ["US" as never],
});
if (usSize.ok) {
  fail("Save must reject a US size");
}

const wrongUsd = saveProductInCatalog(titled.products, "A01", {
  titleEn: "Top — edited",
  titleVn: "Áo",
  descriptionEn: "desc",
  descriptionVn: "desc",
  status: "available",
  priceUsd: 26,
  colors: [],
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
});
if (wrongUsd.ok) {
  fail("A01 Available must reject non-Boss USD");
}

const holdWithUsd = saveProductInCatalog(titled.products, "P02", {
  titleEn: "Thermos",
  titleVn: "Bình",
  descriptionEn: "Hold",
  descriptionVn: "Hold",
  status: "hold",
  priceUsd: 23,
  colors: [],
  images: [{ src: "/products/P02/cover.jpg", colorId: null, order: 1 }],
});
if (holdWithUsd.ok) {
  fail("Hold + USD must be rejected (P02/P05 never $23)");
}

const p05Leak = saveProductInCatalog(titled.products, "P05", {
  titleEn: "Thermos",
  titleVn: "Bình",
  descriptionEn: "Hold",
  descriptionVn: "Hold",
  status: "available",
  priceUsd: 23,
  colors: [],
  images: [{ src: "/products/P05/cover.jpg", colorId: null, order: 1 }],
});
if (p05Leak.ok) {
  fail("P05 $23 must be rejected");
}

// A99 is a sellable mã that never exists in the seed — saving it must fail
// as "not in the catalog" (regression: the old A03 literal went live).
const invent = saveProductInCatalog(titled.products, "A99", holdFields());
if (invent.ok) {
  fail("Save A99 must fail when it is not in the catalog yet");
}
if (!invent.error.includes("not in the catalog")) {
  fail(`Save A99 before Add must say not in the catalog, got ${invent.error}`);
}

const official = saveProductInCatalog(titled.products, "AO001", holdFields());
if (official.ok) {
  fail("Save AO001 must 400");
}

const taken = renameProductInCatalog(titled.products, "A01", "A02", {
  titleEn: "Top — edited",
  titleVn: "Áo",
  descriptionEn: "desc",
  descriptionVn: "desc",
  status: "available",
  priceUsd: 25,
  colors: [],
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
});
if (taken.ok) {
  fail("Renaming onto an existing mã must fail");
}

const hubRename = renameProductInCatalog(titled.products, "A01", "A03", {
  titleEn: "Top — edited",
  titleVn: "Áo",
  descriptionEn: "desc",
  descriptionVn: "desc",
  status: "available",
  priceUsd: 25,
  colors: [],
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
});
if (hubRename.ok) {
  fail("Rename must refuse to move a hub mã off the ten");
}

const invalid = renameProductInCatalog(titled.products, "A01", "Z01", {
  titleEn: "Top",
  titleVn: "Áo",
  descriptionEn: "desc",
  descriptionVn: "desc",
  status: "available",
  priceUsd: 25,
  colors: [],
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
});
if (invalid.ok) {
  fail("Invented letter Z must fail");
}

// Boss-added extra: derive an unused mã from the seed instead of hardcoding
// A04 (live in the catalog now — the old literal created a duplicate).
const extraMa = nextMaForLetter("A", mas);
const extraTarget = nextMaForLetter("A", [...mas, extraMa]);
const leftover: Product[] = [
  ...titled.products,
  {
    ma: extraMa,
    type: "A",
    titleEn: "Leftover",
    titleVn: "Áo",
    descriptionEn: "Boss-added extra",
    descriptionVn: "Thêm",
    status: "hold",
    priceUsd: null,
    qty: 1,
    colors: [],
    images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
    fulfillment: "dropship",
    sourceLink: null,
    sizes: [],
    fitCm: { bustChestCm: null, waistCm: null, lengthCm: null },
  },
];
if (!shopVisibleProducts(leftover).some((product) => product.ma === extraMa)) {
  fail(`Boss-added ${extraMa} must appear on the shop when hold | available`);
}
const saveLeftover = saveProductInCatalog(leftover, extraMa, holdFields());
if (!saveLeftover.ok) {
  fail(`Save leftover ${extraMa} must work, got ${saveLeftover.error}`);
}
const renameExtra = renameProductInCatalog(leftover, extraMa, extraTarget, {
  ...holdFields(),
  images: [{ src: `/products/${extraMa}/cover.jpg`, colorId: null, order: 1 }],
});
if (!renameExtra.ok) {
  fail(`Rename extra ${extraMa} → ${extraTarget} must work, got ${renameExtra.error}`);
}
const renamedExtra = renameExtra.products.find((product) => product.ma === extraTarget);
if (renamedExtra?.images[0]?.src !== `/products/${extraMa}/cover.jpg`) {
  fail("Rename must keep existing photo URLs so thumbs do not 404 after the mã moves");
}
if (renameExtra.products.some((product) => product.ma === extraMa)) {
  fail("Rename must not leave two live SKUs for the same piece");
}
const removedAllowlist = removeProductFromCatalog(leftover, "A01");
if (removedAllowlist.ok) {
  fail("Remove must refuse hub A01 — never invent a replacement");
}
const removedExtra = removeProductFromCatalog(leftover, extraMa);
if (!removedExtra.ok) {
  fail(removedExtra.error);
}
if (removedExtra.products.some((product) => product.ma === extraMa)) {
  fail(`Remove must clean leftover ${extraMa}`);
}

const integrity = inspectCatalogIntegrity(leftover);
if (!integrity.extras.includes(extraMa) || integrity.missingAllowlist.length !== 0) {
  fail(`Integrity must flag leftover ${extraMa} and keep the ten`);
}
if (!looksLikeOfficialMa("AO001") || looksLikeOfficialMa("A01")) {
  fail("Official alphabet is AO001, not A01");
}
try {
  parseProduct({ ...leftover[leftover.length - 1], ma: "AO001", type: "A" }, 0);
  fail("AO001 must not parse onto the sell catalog");
} catch (error) {
  if (!(error instanceof Error) || !error.message.includes("AO001")) {
    fail("Official alphabet error must name AO001");
  }
}
try {
  assertImportSellContract(titled.products.filter((product) => product.ma !== "A01"));
  fail("Import must reject a catalog missing A01");
} catch (error) {
  if (!(error instanceof Error) || !error.message.includes("A01")) {
    fail("Missing-hub import error must name A01");
  }
}
assertImportSellContract(leftover);
assertImportSellContract(added.products);
assertLiveCatalogIntegrity(titled.products);
assertLiveCatalogIntegrity(added.products);
if (isCompleteSaveReceipt({ ok: true })) {
  fail("Incomplete receipt must not look like a Save");
}
if (!silentSaveError().includes("stale")) {
  fail("Silent-save copy must warn the shop may still be stale");
}
if (!isOpaqueRscError("Minified React error #441; visit https://react.dev/errors/441")) {
  fail("React #441 must be treated as an opaque post-Save error");
}
if (!isOpaqueRscError("An error occurred in the Server Components render.")) {
  fail("Server Components render digest must not be toasted");
}
if (isOpaqueRscError("English title is required.")) {
  fail("Real Save errors must still show");
}
if (!opaquePostSaveMessage().includes("Catalog")) {
  fail("Opaque post-Save copy must send Boss to Catalog, not a React overlay");
}

const sold = saveProductInCatalog(titled.products, "A02", {
  titleEn: "Top",
  titleVn: "Áo",
  descriptionEn: "desc",
  descriptionVn: "desc",
  status: "sold",
  priceUsd: 22,
  colors: [],
  images: [{ src: "/products/A02/cover.jpg", colorId: null, order: 1 }],
});
if (!sold.ok) {
  fail(sold.error);
}
if (shopVisibleProducts(sold.products).some((product) => product.ma === "A02")) {
  fail("Sold items must leave the shop");
}

const held = bulkHoldInCatalog(sold.products, ["A01", "S01"]);
if (!held.ok) {
  fail(held.error);
}
const a01 = held.products.find((product) => product.ma === "A01");
const s01 = held.products.find((product) => product.ma === "S01");
if (!a01 || a01.status !== "hold" || a01.priceUsd !== null) {
  fail("Bulk Hold must clear A01 USD");
}
if (!s01 || s01.status !== "hold" || s01.priceUsd !== null) {
  fail("Bulk Hold must clear S01 USD");
}

const seedMas = ["A01", "S01", "P01", "P02", "P03", "P04", "P05", "K01", "H01", "A02"];
for (const ma of seedMas) {
  if (!sold.products.some((product) => product.ma === ma)) {
    fail(`Seed mã ${ma} did not survive`);
  }
}

if (!NON_ALLOWLIST_SAVE_ERROR.includes("400")) {
  fail("Official-alphabet error must be 400-shaped");
}

assertCanonicalSerializedCatalog(
  toCatalogDocumentJson({
    schema: seedDocument.schema,
    version: 1,
    siteId: seedDocument.siteId,
    products: sold.products,
    settings: seedDocument.settings,
  }),
);

if (itemFormHasNativeSaveConfirm()) {
  fail("item-form Add/Edit Save must not native-confirm");
}

const addedMa = savedNextA.products.find((product) => product.ma === nextA);
if (!addedMa) {
  fail(`${nextA} missing after Save`);
}
const addedMaFields = {
  ...holdFields(),
  titleEn: `Top — ${nextA} saved`,
};
if (!liveProductReflectsFields(addedMa, addedMaFields)) {
  fail(`Live ${nextA} must reflect the saved identity fields`);
}
if (liveProductReflectsFields(addedMa, { ...addedMaFields, titleEn: "Other title" })) {
  fail(`Stale live ${nextA} must not count as a Save receipt`);
}

const emptyBody = parseAdminJsonResponse("", 200);
if (
  typeof emptyBody !== "object" ||
  emptyBody === null ||
  (emptyBody as { ok?: unknown }).ok !== false
) {
  fail("Empty Save body must be an error, not a receipt");
}
const htmlBody = parseAdminJsonResponse("<!DOCTYPE html><html>nope</html>", 502);
if (
  typeof htmlBody !== "object" ||
  htmlBody === null ||
  !String((htmlBody as { error?: unknown }).error).includes("not JSON")
) {
  fail("HTML Save body must be a visible not-JSON error");
}
if (!isRecoverableSaveTransportError(silentSaveError())) {
  fail("Incomplete receipt must be recoverable via catalog GET");
}
if (!isRecoverableSaveTransportError("Save returned HTTP 502 that was not JSON.")) {
  fail("HTTP 502 HTML must be recoverable");
}
if (isRecoverableSaveTransportError("English title is required.")) {
  fail("Validation errors must not be treated as transport recovery");
}
if (isRecoverableSaveTransportError("Mã A03 is not in the catalog")) {
  fail("Missing-mã errors must not be treated as transport recovery");
}

console.log("admin-ops smoke ok");

function itemFormHasNativeSaveConfirm(): boolean {
  const source = readFileSync(path.join(process.cwd(), "app/admin/item-form.tsx"), "utf8");
  return source.includes("if (!window.confirm(saveConfirmPrompt(confirmLine)))");
}
