import { readFileSync } from "node:fs";
import path from "node:path";
import {
  addProductToCatalog,
  renameProductInCatalog,
  saveProductInCatalog,
} from "../lib/admin-ops";
import { publicPathsForMas } from "../lib/refresh-shop";
import { parseCatalogDocument } from "../lib/product-parse";
import { PUBLIC_FORBIDDEN_PHRASES, customerStockVoiceHit } from "../lib/public-safety";
import { colorShopLabel, parseProductColor } from "../lib/colors";
import { imagesForColor } from "../lib/product-media";
import type { Product } from "../lib/types";

function fail(message: string): never {
  throw new Error(message);
}

const root = process.cwd();
const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(root, "data", "products.json"), "utf8")) as unknown,
);

const p02 = seed.products.find((product) => product.ma === "P02");
const p05 = seed.products.find((product) => product.ma === "P05");
const a01 = seed.products.find((product) => product.ma === "A01");
if (!p02 || !p05 || !a01) {
  fail("Hub P02 / P05 / A01 missing");
}
if (p02.status !== "hold" || p02.priceUsd !== null || p05.status !== "hold" || p05.priceUsd !== null) {
  fail("P02/P05 must stay Hold with no USD");
}

const holdUsd = saveProductInCatalog(seed.products, "P05", {
  titleEn: p05.titleEn,
  titleVn: p05.titleVn,
  descriptionEn: p05.descriptionEn,
  descriptionVn: p05.descriptionVn,
  status: "hold",
  priceUsd: 23,
  colors: p05.colors,
  images: p05.images,
  fulfillment: p05.fulfillment,
  sourceLink: p05.sourceLink,
});
if (holdUsd.ok) {
  fail("P05 $23 must be rejected");
}

const itemForm = readFileSync(path.join(root, "app/admin/item-form.tsx"), "utf8");
const catalogList = readFileSync(path.join(root, "app/admin/catalog-list.tsx"), "utf8");
const consoleText = readFileSync(path.join(root, "app/admin/console.tsx"), "utf8");
if (!itemForm.includes("admin-rename-input") || !itemForm.includes("Save & change mã")) {
  fail("Edit must expose Change mã (ADM-25)");
}
if (!catalogList.includes("Change mã") || !catalogList.includes("admin-rename-open-")) {
  fail("Catalog list must show Change mã on extras (ADM-25)");
}
if (!consoleText.includes("Change mã")) {
  fail("Admin chrome must name Change mã so testers can find it");
}
if (itemForm.includes("Add <MaMark ma={predictedMa}") || itemForm.includes("→ {nextMaForLetter")) {
  fail("Add must not print next-mã trap tiles (Official #29)");
}
if (!itemForm.includes("Assigned on Save") || !itemForm.includes("Save new mã")) {
  fail("Add stays open; mã is assigned on Save, not advertised as a shop tile");
}

const taken = renameProductInCatalog(seed.products, "A01", "S01", {
  titleEn: a01.titleEn,
  titleVn: a01.titleVn,
  descriptionEn: a01.descriptionEn,
  descriptionVn: a01.descriptionVn,
  status: a01.status,
  priceUsd: a01.priceUsd,
  colors: a01.colors,
  images: a01.images,
  fulfillment: a01.fulfillment,
  sourceLink: a01.sourceLink,
});
if (taken.ok) {
  fail("Rename onto an in-use mã must fail (ADM-26)");
}

const official = renameProductInCatalog(seed.products, "A01", "AO001", {
  titleEn: a01.titleEn,
  titleVn: a01.titleVn,
  descriptionEn: a01.descriptionEn,
  descriptionVn: a01.descriptionVn,
  status: a01.status,
  priceUsd: a01.priceUsd,
  colors: a01.colors,
  images: a01.images,
  fulfillment: a01.fulfillment,
  sourceLink: a01.sourceLink,
});
if (official.ok) {
  fail("Rename to Official AO001 must fail (ADM-26)");
}

const hub = renameProductInCatalog(seed.products, "A01", "A03", {
  titleEn: a01.titleEn,
  titleVn: a01.titleVn,
  descriptionEn: a01.descriptionEn,
  descriptionVn: a01.descriptionVn,
  status: a01.status,
  priceUsd: a01.priceUsd,
  colors: a01.colors,
  images: a01.images,
  fulfillment: a01.fulfillment,
  sourceLink: a01.sourceLink,
});
if (hub.ok) {
  fail("Hub A01 must not rename off the ten (ADM-26)");
}

const leftover: Product[] = [
  ...seed.products,
  {
    ...a01,
    ma: "A04",
    titleEn: "Extra top",
    images: [{ src: "/products/A04/cover.jpg", colorId: null, order: 1 }],
    status: "hold",
    priceUsd: null,
  },
];
const added = addProductToCatalog(seed.products, "A", {
  titleEn: "New hold",
  titleVn: "",
  descriptionEn: "",
  descriptionVn: "",
  status: "hold",
  priceUsd: null,
  colors: [],
  images: [],
});
if (!added.ok || added.ma !== "A03") {
  fail("Add A03 must still Save (Boss override)");
}

const moved = renameProductInCatalog(leftover, "A04", "A03", {
  titleEn: "Extra top",
  titleVn: "",
  descriptionEn: "",
  descriptionVn: "",
  status: "hold",
  priceUsd: null,
  colors: [],
  images: [{ src: "/products/A04/cover.jpg", colorId: null, order: 1 }],
});
if (!moved.ok) {
  fail(`Rename extra A04 → A03 must work, got ${moved.error}`);
}
if (moved.products.some((product) => product.ma === "A04")) {
  fail("Rename must not leave two live SKUs (ADM-28)");
}
if (moved.products.find((product) => product.ma === "A03")?.images[0]?.src !== "/products/A04/cover.jpg") {
  fail("Rename must keep photo bytes at the old folder so thumbs do not 404 (ADM-27)");
}

const paths = publicPathsForMas(["A04", "A03"]);
if (!paths.includes("/m/A04") || !paths.includes("/m/A03")) {
  fail("Save→refresh must revalidate both old and new mã paths (BLOB-03)");
}

const chips = readFileSync(path.join(root, "components/color-name-chips.tsx"), "utf8");
if (chips.includes("backgroundColor") || chips.includes("color.hex") || chips.includes("bg-ink")) {
  fail("Customer color chips must stay text-only gold hairlines (PDP-05)");
}
if (!chips.includes("hairlineLayoutId") || !chips.includes("h-px")) {
  fail("Selected chip keeps a gold h-px inside the outlined box");
}
if (!chips.includes("ky-color-chip")) {
  fail("Color names must sit in a visible outlined box");
}
if (chips.includes("Color ${hex}") || chips.includes("Color #") || chips.includes("color.hex")) {
  fail("Customer chips must not name a color by hex");
}
if (!chips.includes("colorShopLabel") || !chips.includes("aria-label={label}")) {
  fail("Customer chips must expose the word label, not a hue-only square");
}
const gallery = readFileSync(path.join(root, "components/product-gallery.tsx"), "utf8");
if (!gallery.includes("ColorNameChips") || !gallery.includes("GalleryPeekRoll")) {
  fail("Gallery must keep text chips + this-mã peek roll");
}
if (!gallery.includes("imagesForColor") || !gallery.includes("productGalleryReel")) {
  fail("PDP rolls this mã’s unique reel; imagesForColor stays the honesty filter");
}
const roll = readFileSync(path.join(root, "components/gallery-peek-roll.tsx"), "utf8");
if (!roll.includes("pdp-rail") || !roll.includes("data-edge")) {
  fail("Gallery must keep the LEARN 19 snap rail");
}
if (roll.includes("ky-gallery-edge") || roll.includes("ky-frost-start")) {
  fail("Gallery must native-snap without frosting the garment");
}

const labeled = colorShopLabel({ id: "kem", hex: "#F4F0E8", name: "Kem", note: "" }, 0);
if (labeled !== "Kem") {
  fail("Customer color label must be the stored name, not the hex");
}
if (colorShopLabel({ id: "kem", hex: "#F4F0E8", name: "", note: "" }, 0) !== "Color 1") {
  fail("Empty name must print Color 1 — do not invent Kem from hex or slug");
}
if (colorShopLabel({ id: "cxanh01", hex: "#1C2A4A", name: "#1C2A4A", note: "" }, 1) !== "Color 2") {
  fail("A hex stored as the name is still hue-only — use Color 2");
}
const unnamed = parseProductColor({ id: "civory01", hex: "#F4F0E8", name: "", note: "" }, "A01", 0);
if (unnamed.name !== "" || colorShopLabel(unnamed, 0) !== "Color 1") {
  fail("Parse must not invent Ivory/Kem from #F4F0E8");
}

const twoTone: Product = {
  ...a01,
  colors: [
    { id: "kem", hex: "#F4F0E8", name: "Kem", note: "" },
    { id: "xanh", hex: "#7A8B6F", name: "Xanh", note: "" },
  ],
  images: [
    { src: "/products/A01/cover.jpg", colorId: "kem", order: 1 },
    { src: "/products/A01/shared.jpg", colorId: null, order: 2 },
    { src: "/products/A01/xanh.jpg", colorId: "xanh", order: 3 },
  ],
};
const kem = imagesForColor(twoTone, "kem").map((image) => image.src);
if (!kem.includes("/products/A01/cover.jpg") || !kem.includes("/products/A01/shared.jpg")) {
  fail("Selected color must keep tagged ∪ untagged photos on this mã");
}
if (kem.includes("/products/A01/xanh.jpg")) {
  fail("Selected color must not show the other color’s photos");
}

const empty = readFileSync(path.join(root, "components/shop-empty.tsx"), "utf8");
if (!empty.includes("MessengerCta") || !empty.includes('role="status"')) {
  fail("Empty states must stay Message-first with a status region");
}

const shopFiles = [
  "app/(shop)/m/[ma]/page.tsx",
  "components/color-name-chips.tsx",
  "components/product-card.tsx",
  "components/product-price.tsx",
  "components/buy-bar.tsx",
  "components/how-to-buy.tsx",
  "lib/share-card.ts",
];
for (const rel of shopFiles) {
  const text = readFileSync(path.join(root, rel), "utf8");
  for (const phrase of PUBLIC_FORBIDDEN_PHRASES) {
    if (text.includes(phrase)) {
      fail(`${rel} leaks ${phrase}`);
    }
  }
  const stock = customerStockVoiceHit(text);
  if (stock) {
    fail(`${rel} surfaces customer availability copy: ${stock}`);
  }
}

console.log("bugcheck checklist apply ok");
