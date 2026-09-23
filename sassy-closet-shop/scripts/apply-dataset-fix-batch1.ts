/**
 * Boss 2026-09-21: live dataset fix batch 1 — seller/seed colors, binds, sizes, titles.
 * Raw Blob only (readStoredCatalogRecord). No Admin Save. No price changes.
 */
import {
  readStoredCatalogRecord,
  writeLiveCatalogDocument,
} from "../lib/catalog-store";
import seedFile from "../data/products.json";

type Color = { id: string; hex: string; name: string; note?: string };
type Img = { src: string; colorId: string | null; order?: number };
type Prod = {
  ma: string;
  titleEn?: string;
  colors?: Color[];
  sizes?: string[];
  images?: Img[];
};

const seedProducts: Prod[] = Array.isArray(seedFile)
  ? (seedFile as Prod[])
  : ((seedFile as { products: Prod[] }).products ?? []);

const PATCH_MAS = [
  "A01",
  "A02",
  "A04",
  "A07",
  "A13",
  "A15",
  "B02",
  "B03",
  "O01",
  "O02",
  "P02",
  "P03",
  "P05",
  "Q01",
  "S01",
  "S04",
] as const;

const TITLE_OVERRIDES: Record<string, string> = {
  A02: "Polka-dot top",
};

const SIZE_OVERRIDES: Record<string, string[]> = {
  A07: ["2XS", "S", "M", "L"],
};

async function main() {
  const apply = process.argv.includes("--apply");
  const stored = await readStoredCatalogRecord();
  if (!stored || stored.source === "seed") {
    throw new Error("No stored Blob catalog — refusing to write over seed");
  }
  const doc = structuredClone(stored.document);
  const rows: { ma: string; action: string }[] = [];

  for (const ma of PATCH_MAS) {
    const live = doc.products.find((p) => p.ma === ma);
    const seed = seedProducts.find((p) => p.ma === ma);
    if (!live) throw new Error(`missing live ${ma}`);
    if (!seed) {
      rows.push({ ma, action: "skip-no-seed" });
      continue;
    }

    const nextColors = (seed.colors ?? []).map((c) => ({
      id: c.id,
      hex: c.hex,
      name: c.name,
      note: c.note ?? "",
    }));
    const nextImages = (seed.images ?? []).map((img, i) => ({
      src: img.src,
      colorId: img.colorId ?? null,
      order: img.order ?? i + 1,
    }));
    // Prefer live Blob image URLs when seed still has /products/ paths and live has https Blob URLs of same basename count
    const liveImgs = live.images ?? [];
    const mergedImages =
      liveImgs.length > 0
        ? liveImgs.map((img, i) => {
            const seedBind = nextImages[i]?.colorId ?? null;
            // Keep live src (Blob CDN); apply seed bind when seed has one for that index
            return {
              ...img,
              colorId: seedBind ?? img.colorId ?? null,
              order: img.order ?? i + 1,
            };
          })
        : nextImages;

    const nextTitle = TITLE_OVERRIDES[ma] ?? seed.titleEn ?? live.titleEn;
    const nextSizes = SIZE_OVERRIDES[ma] ?? (seed.sizes && seed.sizes.length ? seed.sizes : live.sizes);

    const before = {
      titleEn: live.titleEn,
      colors: (live.colors ?? []).map((c) => c.name).join("|"),
      sizes: (live.sizes ?? []).join("|"),
      binds: (live.images ?? []).map((i) => i.colorId ?? "-").join(","),
    };

    if (apply) {
      if (nextColors.length) live.colors = nextColors;
      if (nextTitle) live.titleEn = nextTitle;
      if (nextSizes) live.sizes = nextSizes;
      live.images = mergedImages;
    }

    const after = {
      titleEn: nextTitle,
      colors: nextColors.map((c) => c.name).join("|") || before.colors,
      sizes: (nextSizes ?? []).join("|"),
      binds: mergedImages.map((i) => i.colorId ?? "-").join(","),
    };
    rows.push({
      ma,
      action: `${before.colors}→${after.colors}; sizes ${before.sizes}→${after.sizes}; title ${before.titleEn}→${after.titleEn}`,
    });
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
  });

  const res = await fetch("https://sassy-closet-shop.vercel.app/api/admin/revalidate", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({}),
  });
  console.log("revalidate", res.status, (await res.text()).slice(0, 180));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
