import {
  addProductToCatalog,
  removeProductFromCatalog,
} from "../lib/admin-ops";
import {
  readLiveCatalogDocument,
  writeLiveCatalog,
} from "../lib/catalog-store";
import { shopVisibleProducts } from "../lib/site-settings";
import type { Product } from "../lib/types";

function holdFields() {
  return {
    titleEn: "Top",
    titleVn: "Áo",
    descriptionEn: "",
    descriptionVn: "",
    status: "hold" as const,
    priceUsd: null,
    colors: [] as Product["colors"],
    images: [] as Product["images"],
  };
}

async function main(): Promise<void> {
  let catalog = (await readLiveCatalogDocument()).products;
  if (catalog.some((product) => product.ma === "A03")) {
    const removed = removeProductFromCatalog(catalog, "A03");
    if (!removed.ok) {
      throw new Error(removed.error);
    }
    await writeLiveCatalog(removed.products);
    catalog = removed.products;
  }

  const added = addProductToCatalog(catalog, "A", holdFields());
  if (!added.ok) {
    throw new Error(`Add A03 failed: ${added.error}`);
  }
  if (added.ma !== "A03") {
    throw new Error(`Expected A03, got ${added.ma}`);
  }
  const written = await writeLiveCatalog(added.products);
  if (!written.blobWritten || !written.catalogSha) {
    throw new Error("Add A03 did not write the live catalog");
  }
  const roundtrip = await readLiveCatalogDocument();
  const row = roundtrip.products.find((product) => product.ma === "A03");
  if (!row) {
    throw new Error("Read-back missing A03");
  }
  if (!shopVisibleProducts(roundtrip.products).some((product) => product.ma === "A03")) {
    throw new Error("A03 is not shop-visible after Add");
  }
  console.log(
    `Add A03 ok ma=${added.ma} blobWritten=${written.blobWritten} sha=${written.catalogSha} updatedAt=${written.updatedAt} backend=${written.backend}`,
  );
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
