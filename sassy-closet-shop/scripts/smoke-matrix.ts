import { readFileSync } from "node:fs";
import path from "node:path";
import {
  addProductToCatalog,
  renameProductInCatalog,
  saveProductInCatalog,
} from "../lib/admin-ops";
import { KNOWN_SEED_MAS } from "../lib/catalog-contract";
import { applyCatalogHandoff } from "../lib/catalog-handoff";
import { HUB_COLORS_BY_MA } from "../lib/hub-colors";
import { HUB_RECORDED_SIZES, recordedHubSourceLink } from "../lib/hub-source-links";
import { htmlHasNextMaTrap } from "../lib/next-ma-trap";
import { parseCatalogDocument } from "../lib/product-parse";
import { isCompleteSaveReceipt, receiptRevalidatedShop } from "../lib/save-receipt";
import { shopSafeProduct } from "../lib/sell-contract";
import { shopVisibleProducts } from "../lib/site-settings";
import type { Product } from "../lib/types";

function fail(message: string): never {
  throw new Error(message);
}

function read(rel: string): string {
  return readFileSync(path.join(process.cwd(), rel), "utf8");
}

const seed = parseCatalogDocument(
  JSON.parse(read(path.join("data", "products.json"))) as unknown,
);

function holdFields() {
  return {
    titleEn: "Top",
    titleVn: "Áo",
    descriptionEn: "One unique top. Message A03 to order — sourced after you inbox.",
    descriptionVn: "Áo độc bản. Nhắn tin A03 để đặt.",
    status: "hold" as const,
    priceUsd: null,
    colors: [] as Product["colors"],
    images: [] as Product["images"],
  };
}

const frame = read("app/admin/frame.tsx");
const itemForm = read("app/admin/item-form.tsx");
const settings = read("app/admin/settings-panel.tsx");
const refresh = read("lib/refresh-shop.ts");
const store = read("lib/catalog-store.ts");
const receipt = read("lib/save-receipt.ts");
const handoff = read("lib/catalog-handoff.ts");
const catalogApi = read("app/api/admin/catalog/route.ts");
const revalidateApi = read("app/api/admin/revalidate/route.ts");
const chips = read("components/color-name-chips.tsx");
const adminColors = read("components/admin-colors.tsx");
const sha = read("lib/catalog-sha.ts");
const css = read("app/globals.css");
const layout = read("app/layout.tsx");
const applyHub = read("scripts/apply-hub-live.ts");
const dropship = read("lib/dropship-copy.ts");

if (!frame.includes('data-save-contract="blob+revalidate"')) {
  fail("O9 Save contract marker missing");
}
if (!receipt.includes("blobWritten") || !receipt.includes("catalogSha") || !receipt.includes("revalidated")) {
  fail("O4 Save receipt shape missing");
}
if (!isCompleteSaveReceipt({
  ok: true,
  blobWritten: true,
  catalogSha: "abcd1234",
  updatedAt: "2026-09-09T00:00:00.000Z",
  revalidated: ["/"],
})) {
  fail("Complete receipt helper drifted");
}
if (
  receiptRevalidatedShop({
    ok: true,
    blobWritten: true,
    catalogSha: "abcd1234",
    updatedAt: "2026-09-09T00:00:00.000Z",
    revalidated: ["/"],
  })
) {
  fail("Import receipt must require /m/A01, not only home");
}
if (
  !receiptRevalidatedShop({
    ok: true,
    blobWritten: true,
    catalogSha: "abcd1234",
    updatedAt: "2026-09-09T00:00:00.000Z",
    revalidated: ["/", "/m/A01"],
  })
) {
  fail("Import receipt must treat / + /m/A01 as shop revalidate");
}
if (!refresh.includes('revalidatePath("/", "page")')) {
  fail("O5 must revalidatePath / page");
}
if (!refresh.includes('revalidatePath("/c/[slug]", "page")')) {
  fail("O5 must revalidatePath /c/[slug] page");
}
if (!refresh.includes('revalidatePath("/m/[ma]", "page")')) {
  fail("O5 must revalidatePath /m/[ma] page");
}
if (!store.includes("hashedImageFileName") || !store.includes("Refusing in-place cover.jpg")) {
  fail("O13 hashed covers missing");
}
if (!sha.includes("searchParams.set(\"v\"") && !sha.includes('params.set("v"')) {
  fail("O13 shop covers must cache-bust with ?v=");
}
if (chips.includes("backgroundColor") || chips.includes("color.hex")) {
  fail("O12 shop colors stay text-only");
}
if (!adminColors.includes("image.colorId") || !adminColors.includes("colorId")) {
  fail("O13 per-color photo bind missing");
}
if (!settings.includes('data-catalog-export="json"') || !settings.includes("Import catalog.v1")) {
  fail("O16/O18 settings Import/Export missing");
}
if (!catalogApi.includes("NO_STORE_HEADERS") || !catalogApi.includes("catalogSha")) {
  fail("O19 GET /api/admin/catalog must be no-store with catalogSha");
}
if (!revalidateApi.includes("refreshShop") || !revalidateApi.includes("405")) {
  fail("O20 POST /api/admin/revalidate must exist; GET 405");
}
if (!handoff.includes("incoming.titleEn.trim() || base.titleEn")) {
  fail("O11 empty kit titles must not wipe shop copy");
}
if (applyHub.includes("xlsx")) {
  fail("catalog:hub must never open Excel");
}
const pkg = read("package.json");
if (/xlsx|exceljs|sheetjs/i.test(pkg)) {
  fail("Shop package must not depend on Excel libraries");
}
if (!read("scripts/smoke-excel-ro.ts").includes("excel-kit")) {
  fail("Excel/OD/intake read-only smoke must stay");
}
if (!dropship.includes("Message to buy")) {
  fail("Hub tiles stay Message-to-buy");
}

const traps = htmlHasNextMaTrap(`${itemForm}\n${read("app/admin/catalog-list.tsx")}`);
if (traps.length > 0) {
  fail(`Next-grid trap tiles must stay off, got ${traps.join(", ")}`);
}
if (!itemForm.includes("Add mã") || !itemForm.includes("Save new mã")) {
  fail("Boss Add stays open as Add mã / Save new mã — not O1 kill");
}

if (!css.includes("--gold: #b08968") || !css.includes("--blush: #f3eee8") || !css.includes("--ink: #111111")) {
  fail("Kelly Ying tokens drifted");
}
if (!layout.includes("Cormorant_Garamond") || !layout.includes("Be_Vietnam_Pro")) {
  fail("Kelly Ying fonts drifted");
}

const added = addProductToCatalog(seed.products, "A", holdFields());
if (!added.ok || added.ma !== "A03") {
  fail(`Boss override: Add A03 must Save, got ${added.ok ? added.ma : added.error}`);
}
if (!shopVisibleProducts(added.products).some((product) => product.ma === "A03")) {
  fail("A03 must be shop-visible after Add (Message-to-buy)");
}
const saved = saveProductInCatalog(added.products, "A03", {
  ...holdFields(),
  titleEn: "Top — A03 matrix",
});
if (!saved.ok) {
  fail(`Save A03 after Add must work, got ${saved.error}`);
}

const leftover: Product[] = [
  ...seed.products,
  {
    ...seed.products[0]!,
    ma: "A04",
    type: "A",
    titleEn: "Extra",
    titleVn: "Áo",
    status: "hold",
    priceUsd: null,
    colors: [],
    images: [{ src: "/products/A04/cover.jpg", colorId: null, order: 1 }],
    sourceLink: null,
  },
];
const renamed = renameProductInCatalog(leftover, "A04", "A03", {
  ...holdFields(),
  images: leftover[leftover.length - 1]!.images,
});
if (!renamed.ok) {
  fail(`Boss override: rename extra A04 → A03 must work, got ${renamed.error}`);
}
const hubOff = renameProductInCatalog(seed.products, "A01", "A03", {
  titleEn: "Top",
  titleVn: "Áo",
  descriptionEn: seed.products[0]!.descriptionEn,
  descriptionVn: seed.products[0]!.descriptionVn,
  status: "available",
  priceUsd: 25,
  colors: seed.products[0]!.colors,
  images: seed.products[0]!.images,
});
if (hubOff.ok) {
  fail("Rename must still refuse moving a hub mã off the ten");
}

const live = {
  ...seed,
  products: added.products,
};
const merged = applyCatalogHandoff(
  live,
  {
    ...seed,
    products: seed.products.map((product) => ({
      ...product,
      titleEn: "",
      titleVn: "",
    })),
  },
  "replace",
  seed.settings,
);
if (merged.products.find((product) => product.ma === "A01")?.titleEn !== "Puppy cardigan") {
  fail("O11 empty JSON titles must keep shop copy");
}
if (!merged.products.some((product) => product.ma === "A03")) {
  fail("Import must keep live extra A03 (Boss override vs kit hard-fail extras)");
}

for (const ma of KNOWN_SEED_MAS) {
  const product = merged.products.find((row) => row.ma === ma);
  if (!product) {
    fail(`Hub ${ma} missing after handoff`);
  }
  const slugs = HUB_COLORS_BY_MA[ma];
  const ids = product.colors.map((color) => color.id);
  if (ids.join(",") !== slugs.join(",")) {
    fail(`Hub ${ma} colors must stay recorded (${slugs.join(",") || "empty"}), got ${ids.join(",") || "empty"}`);
  }
  if (product.sizes.length !== HUB_RECORDED_SIZES[ma].length) {
    fail(`Hub ${ma} sizes must stay empty`);
  }
  const recorded = recordedHubSourceLink(ma);
  if (!recorded || product.sourceLink !== recorded) {
    fail(`Hub ${ma} must stamp the recorded staff link`);
  }
  if (shopSafeProduct(product).sourceLink !== null) {
    fail(`Customer view must strip sourceLink on ${ma}`);
  }
  if ((ma === "P02" || ma === "P05") && (product.status !== "hold" || product.priceUsd !== null)) {
    fail(`${ma} must stay Hold / Inbox for price`);
  }
}

const a03 = merged.products.find((product) => product.ma === "A03");
if (a03?.sourceLink !== null) {
  fail("A03 must not get an invented staff link");
}

console.log("matrix #32 apply ok (Boss override: Add A03 + rename extras; enrich 10)");
