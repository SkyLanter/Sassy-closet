/** Rename H01 Red → Wine on live Blob only (seed already owns image binds). */
import { readStoredCatalogRecord, writeLiveCatalogDocument } from "../lib/catalog-store";

async function main() {
  const stored = await readStoredCatalogRecord();
  if (!stored || stored.source === "seed") {
    throw new Error(`No writable stored catalog (source=${stored?.source})`);
  }
  const doc = stored.document;
  const next = {
    ...doc,
    products: doc.products.map((p) => {
      if (p.ma !== "H01") return p;
      return {
        ...p,
        colors: p.colors.map((c) =>
          c.name.trim().toLowerCase() === "red" ? { ...c, name: "Wine" } : c,
        ),
      };
    }),
  };
  const written = await writeLiveCatalogDocument(next);
  const h = written.document.products.find((p) => p.ma === "H01");
  console.log(JSON.stringify({ colors: h?.colors, images: h?.images }, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
