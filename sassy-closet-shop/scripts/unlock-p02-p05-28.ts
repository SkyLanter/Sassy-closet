import {
  readLiveCatalogDocument,
  writeLiveCatalogDocument,
} from "../lib/catalog-store";

async function main() {
  const doc = await readLiveCatalogDocument();
  for (const ma of ["P02", "P05"] as const) {
    const p = doc.products.find((x) => x.ma === ma);
    if (!p) throw new Error("missing " + ma);
    p.priceUsd = 28;
    p.status = "available";
    console.log("set", ma, p.status, p.priceUsd);
  }
  const result = await writeLiveCatalogDocument(doc);
  console.log(
    "wrote blob",
    "products",
    result.products?.length ?? doc.products.length,
    "blobWritten",
    (result as { blobWritten?: boolean }).blobWritten,
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
