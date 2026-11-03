import { readFileSync } from "node:fs";
import path from "node:path";
import { mergeProductColors, renameProductInCatalog } from "../lib/admin-ops";
import { mergeCatalogDocuments, mergeColorAssets } from "../lib/catalog-merge";
import { reorderImages } from "../lib/image-order";
import {
  asCatalogDocument,
  parseCatalogDocument,
  toCatalogDocumentJson,
} from "../lib/product-parse";
import { assertImportSellContract } from "../lib/sell-contract";
import { productJsonLd } from "../lib/seo";
import type { Product } from "../lib/types";

function fail(message: string): never {
  throw new Error(message);
}

const seedPath = path.join(process.cwd(), "data", "products.json");
const seed = parseCatalogDocument(JSON.parse(readFileSync(seedPath, "utf8")) as unknown);

const twoTone: Product = {
  ...seed.products[0]!,
  ma: "A01",
  type: "A",
  colors: [
    { id: "cblackcolor01", hex: "#111111", name: "Black", note: "" },
    { id: "ccamelcolor01", hex: "#B08968", name: "Camel", note: "" },
  ],
  images: [
    { src: "/products/A01/cover.jpg", colorId: "cblackcolor01", order: 1 },
    { src: "/products/A01/alt.jpg", colorId: "ccamelcolor01", order: 2 },
  ],
};

const catalog = seed.products.map((product) => (product.ma === "A01" ? twoTone : product));

const renamedOff = renameProductInCatalog(catalog, "A01", "A05", {
  titleEn: twoTone.titleEn,
  titleVn: twoTone.titleVn,
  descriptionEn: twoTone.descriptionEn,
  descriptionVn: twoTone.descriptionVn,
  status: twoTone.status,
  priceUsd: twoTone.priceUsd,
  colors: twoTone.colors,
  images: twoTone.images,
});
if (renamedOff.ok) {
  fail("rename onto A05 must 400");
}

const clash = renameProductInCatalog(catalog, "A01", "S01", {
  titleEn: twoTone.titleEn,
  titleVn: twoTone.titleVn,
  descriptionEn: twoTone.descriptionEn,
  descriptionVn: twoTone.descriptionVn,
  status: twoTone.status,
  priceUsd: twoTone.priceUsd,
  colors: twoTone.colors,
  images: twoTone.images,
});
if (clash.ok) {
  fail("rename onto S01 must fail");
}

const letter = renameProductInCatalog(catalog, "A01", "Z01", {
  titleEn: twoTone.titleEn,
  titleVn: twoTone.titleVn,
  descriptionEn: twoTone.descriptionEn,
  descriptionVn: twoTone.descriptionVn,
  status: twoTone.status,
  priceUsd: twoTone.priceUsd,
  colors: twoTone.colors,
  images: twoTone.images,
});
if (letter.ok) {
  fail("invented letter Z must fail");
}

const sameSlot = renameProductInCatalog(catalog, "A01", "A01", {
  titleEn: twoTone.titleEn,
  titleVn: twoTone.titleVn,
  descriptionEn: twoTone.descriptionEn,
  descriptionVn: twoTone.descriptionVn,
  status: twoTone.status,
  priceUsd: twoTone.priceUsd,
  colors: twoTone.colors,
  images: twoTone.images,
});
if (!sameSlot.ok) {
  fail(sameSlot.error);
}

const extra: Product = {
  ...twoTone,
  ma: "A03",
  type: "A",
};
const catalogWithExtra = [...catalog, extra];
const mergedColors = mergeProductColors(catalogWithExtra, "A03", "cblackcolor01", "ccamelcolor01");
if (!mergedColors.ok) {
  fail(mergedColors.error);
}
const mergedExtra = mergedColors.products.find((product) => product.ma === "A03");
if (!mergedExtra || mergedExtra.colors.length !== 1 || mergedExtra.colors[0]?.id !== "cblackcolor01") {
  fail("color merge must drop the source color");
}
if (!mergedExtra.images.every((image) => image.colorId === "cblackcolor01")) {
  fail("color merge must retag photos onto the kept color");
}

const assets = mergeColorAssets(twoTone.colors, twoTone.images, "cblackcolor01", "ccamelcolor01");
if (assets.colors.length !== 1 || assets.images.filter((image) => image.colorId === "cblackcolor01").length !== 2) {
  fail("mergeColorAssets should retag every dropped photo");
}

try {
  mergeColorAssets(twoTone.colors, twoTone.images, "cblackcolor01", "cblackcolor01");
  fail("same-id color merge must throw");
} catch (error) {
  if (!(error instanceof Error) || !error.message.includes("different")) {
    fail("wrong error for same-id merge");
  }
}

const incoming = asCatalogDocument(
  [
    {
      ...twoTone,
      titleEn: "Top — official overlay",
      priceUsd: 25,
    },
    {
      ...seed.products.find((product) => product.ma === "P02")!,
      titleEn: "Thermos — overlay",
    },
  ],
  { announcementLines: ["Official overlay"], facebookPageUrl: seed.settings.facebookPageUrl },
  "sassy-closet-official",
);

const mergedDoc = mergeCatalogDocuments(seed, incoming);
if (mergedDoc.products.length !== seed.products.length) {
  fail("subset merge must keep every base mã");
}
const overlayA01 = mergedDoc.products.find((product) => product.ma === "A01");
if (overlayA01?.titleEn !== "Top — official overlay") {
  fail("merge must overlay matching mãs");
}
const overlayP02 = mergedDoc.products.find((product) => product.ma === "P02");
if (overlayP02?.titleEn !== "Thermos — overlay") {
  fail("merge must overlay P02");
}
if (overlayP02?.status !== "hold" || overlayP02.priceUsd !== null) {
  fail("merge must not invent a USD on Hold");
}
if (mergedDoc.settings.announcementLines[0] !== "Official overlay") {
  fail("merge takes incoming settings");
}
if (mergedDoc.siteId !== "sassy-closet-shop") {
  fail(`merge must stamp the runtime siteId, got ${mergedDoc.siteId}`);
}

const extraIncoming = asCatalogDocument(
  [
    ...incoming.products,
    {
      ma: "A03",
      type: "A",
      titleEn: "Added on official",
      titleVn: "Áo",
      descriptionEn: "One extra top from official.",
      descriptionVn: "Áo thêm.",
      qty: 1,
      status: "hold",
      priceUsd: null,
      colors: [],
      images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
      fulfillment: "dropship",
      sourceLink: null,
      sizes: [],
      fitCm: { bustChestCm: null, waistCm: null, lengthCm: null },
    },
  ],
  incoming.settings,
  "sassy-closet-official",
);
const withExtra = mergeCatalogDocuments(seed, extraIncoming);
if (!withExtra.products.some((product) => product.ma === "A03")) {
  fail("merge must add a new valid mã from incoming");
}
if (withExtra.products.length !== 11) {
  fail(`expected 11 mãs after adding A03, got ${withExtra.products.length}`);
}
assertImportSellContract(withExtra.products);

const reordered = reorderImages(
  [
    { src: "a", colorId: null, order: 1 },
    { src: "b", colorId: null, order: 1 },
    { src: "c", colorId: null, order: 1 },
  ],
  0,
  1,
);
if (reordered.map((image) => image.src).join("") !== "bac") {
  fail("reorder 0→1 should swap the first two");
}
const clamped = reorderImages([{ src: "a", colorId: null, order: 1 }], 0, -1);
if (clamped[0]?.src !== "a") {
  fail("reorder must no-op at the edge");
}

const holdLd = productJsonLd(seed.products.find((product) => product.ma === "P02")!);
const holdOffer = holdLd.offers;
if (
  holdOffer &&
  typeof holdOffer === "object" &&
  "price" in holdOffer
) {
  fail("Hold JSON-LD must not invent a USD price");
}

toCatalogDocumentJson(mergedDoc);
console.log("rename/merge unit ok", {
  mergedColors: mergedExtra.colors.map((color) => color.name).join(","),
  mergedCount: mergedDoc.products.length,
  withExtra: withExtra.products.map((product) => product.ma).join(","),
});
