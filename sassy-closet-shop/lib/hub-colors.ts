import { isKnownSeedMa } from "@/lib/catalog-contract";
import { isColorId } from "@/lib/colors";
import { normalizeMa } from "@/lib/ma";
import type { Product, ProductColor, ProductImageAsset } from "@/lib/types";

/** Recorded hub slugs — not a mood board. Do not invent `den` on K01. */
export const HUB_COLOR_SLUGS = ["kem", "xanh", "hoa", "do", "den", "hong", "cham-bi"] as const;

export type HubColorSlug = (typeof HUB_COLOR_SLUGS)[number];

export const HUB_COLORS_BY_MA: Readonly<Record<string, readonly HubColorSlug[]>> = {
  // Boss 2026-09-21: seller SKU is color truth — do not force old GF hub slugs.
  // Empty = keep Blob/seed colors (Yellow/Purple, Off-white, character SKUs, etc.).
  A01: [],
  S01: [],
  P01: ["hoa"],
  P02: [],
  P03: [],
  P04: ["kem"],
  P05: [],
  K01: [],
  H01: [],
  A02: [],
};

const SLUG_NAME: Readonly<Record<HubColorSlug, string>> = {
  kem: "Kem",
  xanh: "Xanh",
  hoa: "Hoa",
  do: "Đỏ",
  den: "Đen",
  hong: "Hồng",
  "cham-bi": "Chấm bi",
};

const SLUG_HEX: Readonly<Record<HubColorSlug, string>> = {
  kem: "#F4F0E8",
  xanh: "#1C2A4A",
  hoa: "#C4A484",
  do: "#8B3A3A",
  den: "#111111",
  hong: "#E8D5C4",
  "cham-bi": "#6B6B6B",
};

const NAME_TO_SLUG: Readonly<Record<string, HubColorSlug>> = {
  kem: "kem",
  xanh: "xanh",
  hoa: "hoa",
  do: "do",
  den: "den",
  hong: "hong",
  "cham-bi": "cham-bi",
  "chấm bi": "cham-bi",
  "cham bi": "cham-bi",
  đỏ: "do",
  đen: "den",
  hồng: "hong",
};

export function isHubColorSlug(value: string): value is HubColorSlug {
  return (HUB_COLOR_SLUGS as readonly string[]).includes(value);
}

export function recordedHubSlugs(ma: string): readonly HubColorSlug[] {
  return HUB_COLORS_BY_MA[normalizeMa(ma)] ?? [];
}

export function hubColorLocked(ma: string): boolean {
  return isKnownSeedMa(normalizeMa(ma));
}

export function slugFromColorName(name: string): HubColorSlug | null {
  const key = name.trim().toLocaleLowerCase("vi");
  return NAME_TO_SLUG[key] ?? null;
}

export function hubColorRecord(slug: HubColorSlug): ProductColor {
  return {
    id: slug,
    hex: SLUG_HEX[slug],
    name: SLUG_NAME[slug],
    note: "",
  };
}

/** Null unless the slug already exists on this mã. Never invent a bind. */
export function bindColorId(colors: ProductColor[], colorId: string | null): string | null {
  if (colorId === null || !colorId.trim()) {
    return null;
  }
  const trimmed = colorId.trim();
  if (!isColorId(trimmed)) {
    return null;
  }
  return colors.some((color) => color.id === trimmed) ? trimmed : null;
}

export function nextImageOrder(images: Array<{ order?: number }>): number {
  let max = 0;
  for (const image of images) {
    if (typeof image.order === "number" && Number.isFinite(image.order) && image.order > max) {
      max = image.order;
    }
  }
  return max + 1;
}

export function stampImageOrders(images: ProductImageAsset[]): ProductImageAsset[] {
  return images.map((image, index) => ({ ...image, order: index + 1 }));
}

export function sortImagesByOrder(images: ProductImageAsset[]): ProductImageAsset[] {
  return stampImageOrders(
    images
      .map((image, index) => ({ image, index }))
      .sort((left, right) => {
        const a = left.image.order;
        const b = right.image.order;
        if (a !== b) {
          return a - b;
        }
        return left.index - right.index;
      })
      .map((row) => row.image),
  );
}

/** Remap leftover generated ids onto hub slugs. Do not invent colors on K01/H01. */
export function applyRecordedHubColors(product: Product): Product {
  const slugs = recordedHubSlugs(product.ma);
  if (!hubColorLocked(product.ma)) {
    return product;
  }
  if (slugs.length === 0) {
    const colors = product.colors.filter(
      (color) => !isHubColorSlug(color.id) && slugFromColorName(color.name) === null,
    );
    const allowed = new Set(colors.map((color) => color.id));
    const images = sortImagesByOrder(
      product.images.map((image) => ({
        ...image,
        colorId: image.colorId && allowed.has(image.colorId) ? image.colorId : null,
      })),
    );
    return { ...product, colors, images };
  }

  const bySlug = new Map<HubColorSlug, ProductColor>();
  const idMap = new Map<string, HubColorSlug>();
  for (const color of product.colors) {
    const slug = isHubColorSlug(color.id) ? color.id : slugFromColorName(color.name);
    if (!slug || !slugs.includes(slug)) {
      continue;
    }
    idMap.set(color.id, slug);
    if (!bySlug.has(slug)) {
      bySlug.set(slug, {
        id: slug,
        hex: color.hex || SLUG_HEX[slug],
        name: SLUG_NAME[slug],
        note: color.note,
      });
    }
  }
  for (const slug of slugs) {
    if (!bySlug.has(slug)) {
      bySlug.set(slug, hubColorRecord(slug));
    }
  }
  const colors = slugs.map((slug) => bySlug.get(slug) ?? hubColorRecord(slug));
  const images = sortImagesByOrder(
    product.images.map((image) => {
      if (image.colorId === null) {
        return image;
      }
      const mapped = idMap.get(image.colorId);
      const nextId = mapped && colors.some((color) => color.id === mapped) ? mapped : bindColorId(colors, image.colorId);
      return { ...image, colorId: nextId };
    }),
  );
  return { ...product, colors, images };
}
