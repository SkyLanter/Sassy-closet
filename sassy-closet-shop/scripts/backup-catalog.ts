import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { catalogExportFilename } from "../lib/catalog-contract";
import { assertHandoffJson, toHandoffCatalogJson } from "../lib/catalog-handoff";
import { readStoredCatalogRecord } from "../lib/catalog-store";

async function main(): Promise<void> {
  const stored = await readStoredCatalogRecord();
  if (!stored) {
    throw new Error("No stored catalog to back up (Blob/KV/local).");
  }
  const document = stored.document;
  const json = toHandoffCatalogJson(document);
  assertHandoffJson(json);
  const dir = path.join(process.cwd(), "data", "backups");
  mkdirSync(dir, { recursive: true });
  const dest = path.join(dir, catalogExportFilename(document.siteId));
  writeFileSync(dest, json);
  console.log(
    `catalog backup ${dest} (${document.products.length} mãs, schema ${document.schema}, source ${stored.source})`,
  );
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
