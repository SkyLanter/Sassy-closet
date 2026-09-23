/**
 * Patch live Blob H01 only: Wine rename + chip→photo binds.
 * Does not invent colors. Does not touch other mãs.
 */
import { readLiveCatalogDocument, writeLiveCatalogDocument } from "../lib/catalog-store";

async function main() {
  const doc = await readLiveCatalogDocument();
  const idx = doc.products.findIndex((p) => p.ma === "H01");
  if (idx < 0) throw new Error("H01 missing from live catalog");
  const h01 = { ...doc.products[idx]! };
  h01.colors = h01.colors.map((c) =>
    c.name.trim().toLowerCase() === "red" ? { ...c, name: "Wine" } : c,
  );
  const pink = h01.colors.find((c) => c.name === "Pink")?.id;
  const blue = h01.colors.find((c) => c.name === "Blue")?.id;
  const wine = h01.colors.find((c) => c.name === "Wine")?.id;
  if (!pink || !blue || !wine) {
    throw new Error(`H01 color ids incomplete pink=${pink} blue=${blue} wine=${wine}`);
  }
  h01.images = h01.images.map((im) => {
    const src = im.src;
    if (src.endsWith("/cover.jpg") || src.endsWith("cover.jpg")) {
      return { ...im, colorId: wine };
    }
    if (src.includes("photo-2")) return { ...im, colorId: blue };
    if (src.includes("photo-3")) return { ...im, colorId: pink };
    return im;
  });
  const next = {
    ...doc,
    products: doc.products.map((p, i) => (i === idx ? h01 : p)),
  };
  const written = await writeLiveCatalogDocument(next);
  const out = written.document.products.find((p) => p.ma === "H01");
  console.log(
    JSON.stringify(
      {
        ok: true,
        backend: written.backend,
        sha: written.catalogSha,
        colors: out?.colors,
        images: out?.images,
      },
      null,
      2,
    ),
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
