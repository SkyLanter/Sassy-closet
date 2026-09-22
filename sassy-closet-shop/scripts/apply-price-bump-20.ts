/**
 * Boss 2026-09-21: bump 20 mãs +$1 to 30% ceil.
 * Reads RAW stored Blob (no hub color overlay). Only mutates priceUsd.
 */
import {
  readStoredCatalogRecord,
  writeLiveCatalogDocument,
} from "../lib/catalog-store";

const BUMPS: Record<string, { before: number; target: number }> = {
  A01: { before: 29, target: 30 },
  A02: { before: 25, target: 26 },
  A04: { before: 23, target: 24 },
  A07: { before: 28, target: 29 },
  A09: { before: 28, target: 29 },
  A10: { before: 31, target: 32 },
  A11: { before: 29, target: 30 },
  A12: { before: 32, target: 33 },
  A13: { before: 27, target: 28 },
  A14: { before: 26, target: 27 },
  A15: { before: 27, target: 28 },
  B03: { before: 67, target: 68 },
  J01: { before: 32, target: 33 },
  K01: { before: 39, target: 40 },
  O01: { before: 21, target: 22 },
  O03: { before: 6, target: 7 },
  O05: { before: 14, target: 15 },
  P04: { before: 11, target: 12 },
  S01: { before: 44, target: 45 },
  S03: { before: 29, target: 30 },
};

async function main() {
  const apply = process.argv.includes("--apply");
  const stored = await readStoredCatalogRecord();
  if (!stored || stored.source === "seed") {
    throw new Error("No stored Blob catalog — refusing to write over seed");
  }
  const doc = structuredClone(stored.document);
  const rows: { ma: string; live: number | null; action: string }[] = [];

  for (const [ma, { before, target }] of Object.entries(BUMPS)) {
    const p = doc.products.find((x) => x.ma === ma);
    if (!p) throw new Error(`missing ${ma}`);
    const live = p.priceUsd;
    if (live === target) {
      rows.push({ ma, live, action: "skip-already-target" });
      continue;
    }
    if (live !== before) {
      throw new Error(`${ma} stored $${live} ≠ before $${before} (and not target $${target}) — abort`);
    }
    if (apply) p.priceUsd = target;
    rows.push({ ma, live, action: apply ? `set→${target}` : `dry-run→${target}` });
  }

  console.table(rows);
  if (!apply) {
    console.log("Dry run only. Re-run with --apply to write Blob.");
    return;
  }

  doc.updatedAt = new Date().toISOString();
  const result = await writeLiveCatalogDocument(doc);
  console.log("wrote", {
    backend: (result as { backend?: string }).backend,
    catalogSha: (result as { catalogSha?: string }).catalogSha,
    products: result.document?.products?.length ?? doc.products.length,
  });

  try {
    const res = await fetch("https://sassy-closet-shop.vercel.app/api/admin/revalidate", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({}),
    });
    console.log("revalidate", res.status, (await res.text()).slice(0, 200));
  } catch (e) {
    console.warn("revalidate failed:", e);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
