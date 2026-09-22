import { readFileSync } from "node:fs";
import path from "node:path";
import { applyCatalogHandoff, assertHandoffJson, roundTripHandoffCatalog, toHandoffCatalogJson } from "../lib/catalog-handoff";
import { assertImportableHandoffJson } from "../lib/handoff-json";
import { isKnownSeedMa, KNOWN_SEED_MAS } from "../lib/catalog-contract";
import { HUB_RECORDED_SIZES, recordedHubSourceLink } from "../lib/hub-source-links";
import { parseCatalogDocument } from "../lib/product-parse";
import { assertImportSellContract, shopSafeProduct } from "../lib/sell-contract";
import type { CatalogDocument } from "../lib/types";

function fail(message: string): never {
  throw new Error(message);
}

const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(process.cwd(), "data", "products.json"), "utf8")) as unknown,
);

const liveWithExtra: CatalogDocument = {
  ...seed,
  products: [
    ...seed.products,
    {
      ...seed.products[0]!,
      ma: "A03",
      type: "A",
      titleEn: "Top — live extra",
      titleVn: "Áo",
      status: "hold",
      priceUsd: null,
      colors: [],
      images: [],
    },
  ],
};

const kit = {
  schema: "catalog.v1",
  source: "Documents/Sassy Closet/sassycloset.xlsx",
  exportedAt: "2026-09-09T01:42:55Z",
  allowlist: [...KNOWN_SEED_MAS],
  products: seed.products.map((product) => ({
    ma: product.ma,
    type: product.ma === "P02" || product.ma === "P05" ? "thermos" : product.ma === "A01" ? "top" : product.type,
    titleEn: "",
    titleVn: "",
    descriptionEn: "",
    descriptionVn: "",
    status: product.status,
    priceUsd: product.priceUsd,
    qty: 1,
    colors: product.colors.map((color) => ({ id: color.id, name: color.name })),
    images: [
      {
        src: `Documents/Sassy Closet/Photos/${product.ma}/001.jpg`,
        colorId: null,
        order: 1,
      },
    ],
  })),
};

const parsedKit = parseCatalogDocument(kit);
if (parsedKit.products[0]?.titleEn !== "") {
  fail("Kit empty titles must parse");
}
if (parsedKit.products.some((product) => product.images.some((image) => image.src.includes("Documents")))) {
  fail("OneDrive photo paths must not enter the shop catalog");
}
if (parsedKit.products.find((product) => product.ma === "A01")?.colors[0]?.id !== "kem") {
  fail("Kit kem without hex must keep the hub slug");
}

const replaced = applyCatalogHandoff(liveWithExtra, parsedKit, "replace", liveWithExtra.settings);
if (!replaced.products.some((product) => product.ma === "A03" && product.titleEn === "Top — live extra")) {
  fail("Replace kit JSON must keep live extra A03");
}
const replacedA01 = replaced.products.find((product) => product.ma === "A01");
if (!replacedA01 || replacedA01.titleEn !== "Puppy cardigan") {
  fail("Empty kit title must keep shop copy on A01");
}
if (!replacedA01.images[0]?.src.startsWith("/products/A01/")) {
  fail("Empty kit images after OD drop must keep shop cover");
}
if (replaced.products.find((product) => product.ma === "P02")?.priceUsd !== null) {
  fail("P02 stays Hold");
}

assertImportSellContract(replaced.products);

const exported = toHandoffCatalogJson(replaced);
assertHandoffJson(exported);
if (!exported.includes(`"allowlist"`) || !exported.includes("A01")) {
  fail("Handoff export must include allowlist");
}
if (exported.includes("sassycloset.xlsx")) {
  fail("Shop export must not write the OneDrive xlsx path");
}

const roundTripped = roundTripHandoffCatalog(liveWithExtra);
if (!roundTripped.products.some((product) => product.ma === "A03" && product.titleEn === "Top — live extra")) {
  fail("Export round-trip must keep live extra A03");
}
if (roundTripped.products.find((product) => product.ma === "P02")?.priceUsd !== null) {
  fail("Export round-trip must keep P02 Inbox for price");
}

try {
  assertHandoffJson("<!doctype html><html><body>ok</html>");
  fail("HTML must not pass as a shop export");
} catch (error) {
  if (!(error instanceof Error) || !error.message.toLowerCase().includes("json")) {
    fail("HTML export error must name JSON");
  }
}

assertImportableHandoffJson(JSON.stringify(kit));
try {
  assertHandoffJson(JSON.stringify(kit));
  fail("Kit with OneDrive xlsx source must not pass as a shop export");
} catch (error) {
  if (!(error instanceof Error) || !error.message.toLowerCase().includes("xlsx")) {
    fail("Shop export must refuse the OneDrive xlsx path");
  }
}

try {
  parseCatalogDocument({
    ...kit,
    allowlist: ["A01", "A03"],
  });
  fail("Wrong allowlist must fail");
} catch (error) {
  if (!(error instanceof Error) || !error.message.includes("allowlist")) {
    fail("Wrong allowlist error");
  }
}

try {
  parseCatalogDocument({
    schema: "catalog.v1",
    products: [{ ...seed.products[0], ma: "AO001", type: "A" }],
    settings: seed.settings,
  });
  fail("AO001 must not import");
} catch (error) {
  if (!(error instanceof Error) || !error.message.includes("AO001")) {
    fail("Official alphabet import error must name AO001");
  }
}

const hubCopy = applyCatalogHandoff(liveWithExtra, seed, "replace", liveWithExtra.settings);
if (hubCopy.products.filter((product) => isKnownSeedMa(product.ma)).length !== 10) {
  fail("Hub copy must keep the ten seed mãs");
}
if (!hubCopy.products.some((product) => product.ma === "A03")) {
  fail("Hub copy must keep live extra A03");
}
for (const ma of KNOWN_SEED_MAS) {
  const product = hubCopy.products.find((row) => row.ma === ma);
  const recorded = recordedHubSourceLink(ma);
  if (!product || !recorded || product.sourceLink !== recorded) {
    fail(`Hub copy must stamp the recorded staff link on ${ma}`);
  }
  if (product.sizes.length !== HUB_RECORDED_SIZES[ma].length) {
    fail(`Hub ${ma} must keep empty sizes — All sheet has no size column`);
  }
  if (shopSafeProduct(product).sourceLink !== null) {
    fail(`Customer view must strip the staff link on ${ma}`);
  }
}
if (hubCopy.products.find((product) => product.ma === "A03")?.sourceLink !== null) {
  fail("A03 must not get an invented staff link");
}
if (hubCopy.products.find((product) => product.ma === "P05")?.priceUsd !== null) {
  fail("P05 stays Hold — do not copy a hub sell dollar");
}

const applyHub = readFileSync(path.join(process.cwd(), "scripts/apply-hub-live.ts"), "utf8");
if (!applyHub.includes("applyCatalogHandoff") || applyHub.includes("xlsx")) {
  fail("catalog:hub must copy seed into the sell catalog — never Excel");
}

console.log("catalog handoff smoke ok");
