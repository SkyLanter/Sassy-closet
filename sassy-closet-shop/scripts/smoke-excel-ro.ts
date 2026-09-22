import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { catalogExportFilename, CATALOG_SCHEMA } from "../lib/catalog-contract";
import { toHandoffCatalogJson } from "../lib/catalog-handoff";
import { assertHandoffExportText } from "../lib/handoff-json";
import { isHqDiskPhotoPath } from "../lib/kit-catalog";
import { parseCatalogDocument } from "../lib/product-parse";

function fail(message: string): never {
  throw new Error(message);
}

const root = process.cwd();

function read(rel: string): string {
  return readFileSync(path.join(root, rel), "utf8");
}

if (existsSync(path.join(root, "excel-kit"))) {
  fail("excel-kit/ must not land in the sell-test shop");
}
if (existsSync(path.join(root, "sassy-closet"))) {
  fail("intake sassy-closet/ must not land in the sell-test shop");
}
const gitignore = read(".gitignore");
if (!gitignore.includes("/sassy-closet/") || !gitignore.includes("/excel-kit/")) {
  fail("gitignore must keep intake and excel-kit out of the sell-test shop");
}

function walkFiles(rel: string, acc: string[]): void {
  const full = path.join(root, rel);
  if (!existsSync(full)) {
    return;
  }
  const stat = statSync(full);
  if (stat.isDirectory()) {
    for (const name of readdirSync(full)) {
      if (name === "node_modules" || name === ".next" || name === ".git") {
        continue;
      }
      walkFiles(path.join(rel, name), acc);
    }
    return;
  }
  if (/\.xlsx$/i.test(rel)) {
    fail(`Shop must not ship an Excel workbook (${rel})`);
  }
  if (/\.(ts|tsx|js|mjs|cjs|json)$/.test(rel)) {
    acc.push(rel);
  }
}

const codeFiles: string[] = [];
for (const dir of ["app", "lib", "scripts", "components", "data"]) {
  walkFiles(dir, codeFiles);
}

const pkg = read("package.json");
if (/xlsx|exceljs|sheetjs|node-xlsx/i.test(pkg)) {
  fail("Shop package must not depend on Excel libraries");
}

const applyHub = read("scripts/apply-hub-live.ts");
if (applyHub.includes("xlsx") || applyHub.includes("excel-kit") || applyHub.includes("store.json")) {
  fail("catalog:hub must never open Excel, intake, or store.json");
}

const store = read("lib/catalog-store.ts");
if (store.includes("store.json")) {
  fail("Sell catalog must not mention intake store.json");
}
if (!store.includes('path.join("data", "live-catalog.json")')) {
  fail("Local persist must be data/live-catalog.json — never Official xlsx");
}

const handoffJson = read("lib/handoff-json.ts");
if (!handoffJson.includes("sassycloset") || !handoffJson.includes("must not write")) {
  fail("Handoff export must refuse the OneDrive xlsx path");
}
if (!read("lib/catalog-handoff.ts").includes("assertHandoffExportText")) {
  fail("Handoff JSON export must run the xlsx refuse");
}

try {
  assertHandoffExportText(
    JSON.stringify({
      schema: CATALOG_SCHEMA,
      products: [{ ma: "A01" }],
      allowlist: ["A01"],
      source: "Documents/Sassy Closet/sassycloset.xlsx",
    }),
  );
  fail("Export with sassycloset.xlsx source must throw");
} catch (error) {
  if (!(error instanceof Error) || !error.message.toLowerCase().includes("xlsx")) {
    fail("Handoff export error must name the xlsx path");
  }
}

const exportRoute = read("app/api/admin/catalog/export/route.ts");
if (!exportRoute.includes("application/json") || exportRoute.includes("xlsx")) {
  fail("Catalog export must be catalog.v1 JSON, never Excel");
}

const filename = catalogExportFilename();
if (!filename.endsWith(".json") || /xlsx/i.test(filename)) {
  fail(`Export filename must be JSON, got ${filename}`);
}

if (!isHqDiskPhotoPath("Documents/Sassy Closet/Photos/A01/001.jpg")) {
  fail("OneDrive HQ photo paths must be dropped on parse");
}
if (!isHqDiskPhotoPath("https://onedrive.live.com/redir?resid=A01")) {
  fail("onedrive.live.com URLs must be dropped on parse");
}

const excelImport = /\bfrom\s+["']xlsx["']|\bfrom\s+["']exceljs["']|require\(\s*["']xlsx["']\)/;
for (const rel of codeFiles) {
  const text = read(rel);
  if (excelImport.test(text)) {
    fail(`${rel} imports an Excel library`);
  }
  if (rel.startsWith("docs/")) {
    continue;
  }
  if (
    !rel.startsWith("scripts/smoke-") &&
    !rel.startsWith("scripts/prove-") &&
    /writeFile(Sync)?|createWriteStream/.test(text) &&
    /\.xlsx|sassycloset/i.test(text)
  ) {
    fail(`${rel} looks like it writes Excel / OneDrive`);
  }
}

const seed = parseCatalogDocument(
  JSON.parse(read(path.join("data", "products.json"))) as unknown,
);
const exported = toHandoffCatalogJson(seed);
if (/sassycloset\.xlsx|OneDrive|excel-kit|store\.json/i.test(exported)) {
  fail("Shop catalog.v1 export must not write Excel, OneDrive, or intake paths");
}

console.log("excel / OneDrive / intake read-only ok");
