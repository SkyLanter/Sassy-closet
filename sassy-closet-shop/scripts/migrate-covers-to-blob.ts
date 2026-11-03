/**
 * Migrate external product cover URLs (Catbox, Alicdn, …) to Vercel Blob.
 *
 * Usage:
 *   npx tsx --require ./scripts/alias.cjs scripts/migrate-covers-to-blob.ts [--dry-run] [--ma D05]
 *
 * --dry-run (default): list external covers without fetching or uploading.
 * --live: fetch each external cover, upload to Blob, rewrite the live catalog.
 * --ma <MÃ>: only migrate this mã (repeatable).
 *
 * Requires BLOB_READ_WRITE_TOKEN for --live. Reads the live catalog
 * (Blob/KV/local/seed via readStoredCatalogRecord) and writes back through
 * writeLiveCatalogDocument so the same integrity gates apply.
 *
 * Draft PR only — never run --live without Boss's exact yes.
 */
import { put } from "@vercel/blob";
import {
  fetchImageBytes,
  isExternalCoverUrl,
  migrateExternalCoversToBlob,
  type ImageBlobPort,
} from "../lib/photo-migrate";
import {
  readStoredCatalogRecord,
  writeLiveCatalogDocument,
} from "../lib/catalog-store";
import { parseCatalogDocument } from "../lib/product-parse";

function fail(message: string): never {
  console.error(`[migrate-covers] ${message}`);
  process.exit(1);
}

function parseArgs(): { live: boolean; mas: string[] } {
  const args = process.argv.slice(2);
  const live = args.includes("--live");
  const mas: string[] = [];
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--ma" && args[i + 1]) {
      mas.push(args[i + 1].trim().toUpperCase());
      i += 1;
    }
  }
  return { live, mas };
}

function createVercelImagePort(): ImageBlobPort {
  return {
    async putImage(pathname, bytes, contentType) {
      const blob = await put(pathname, bytes, {
        access: "public",
        addRandomSuffix: true,
        contentType,
      });
      return { url: blob.url };
    },
  };
}

async function main(): Promise<void> {
  const { live, mas } = parseArgs();
  const onlyMas = new Set(mas);

  const record = await readStoredCatalogRecord();
  if (!record) {
    fail("No stored catalog found (Blob/KV/local). Nothing to migrate.");
  }
  const document = parseCatalogDocument(record.document);
  console.log(`[migrate-covers] source=${record.source} products=${document.products.length}`);

  const externals: { ma: string; src: string }[] = [];
  for (const product of document.products) {
    if (onlyMas.size > 0 && !onlyMas.has(product.ma)) {
      continue;
    }
    for (const image of product.images) {
      if (isExternalCoverUrl(image.src)) {
        externals.push({ ma: product.ma, src: image.src });
      }
    }
  }

  if (externals.length === 0) {
    console.log("[migrate-covers] No external covers found. Blob-first already holds.");
    return;
  }

  console.log(`[migrate-covers] External covers found: ${externals.length}`);
  for (const { ma, src } of externals) {
    console.log(`  ${ma}: ${src.slice(0, 90)}`);
  }

  if (!live) {
    console.log("[migrate-covers] Dry run — pass --live to fetch, upload, and rewrite.");
    return;
  }

  if (!process.env.BLOB_READ_WRITE_TOKEN?.trim()) {
    fail("BLOB_READ_WRITE_TOKEN is required for --live.");
  }

  const scoped = {
    ...document,
    products: onlyMas.size > 0
      ? document.products.filter((p) => onlyMas.has(p.ma))
      : document.products,
  };
  const { document: migrated, report } = await migrateExternalCoversToBlob(
    scoped,
    createVercelImagePort(),
    fetchImageBytes,
  );

  console.log(`[migrate-covers] migrated=${report.migrated.length} skipped=${report.skipped.length} errors=${report.errors.length}`);
  for (const m of report.migrated) {
    console.log(`  OK ${m.ma}: ${m.from.slice(0, 60)} -> ${m.to.slice(0, 80)}`);
  }
  for (const s of report.skipped) {
    console.log(`  SKIP ${s.ma}: ${s.reason} ${s.src.slice(0, 60)}`);
  }
  for (const e of report.errors) {
    console.log(`  ERR ${e.ma}: ${e.error} ${e.src.slice(0, 60)}`);
  }

  if (report.migrated.length === 0) {
    console.log("[migrate-covers] Nothing migrated — catalog unchanged.");
    return;
  }

  // Merge migrated products back into the full document.
  const migratedByMa = new Map(migrated.products.map((p) => [p.ma, p]));
  const next = {
    ...document,
    products: document.products.map((p) => migratedByMa.get(p.ma) ?? p),
  };
  const result = await writeLiveCatalogDocument(parseCatalogDocument(next));
  console.log(`[migrate-covers] Catalog rewritten via ${result.backend}. sha=${result.catalogSha.slice(0, 12)}`);
}

main().catch((error) => {
  console.error("[migrate-covers] fatal", error instanceof Error ? error.message : error);
  process.exit(1);
});
