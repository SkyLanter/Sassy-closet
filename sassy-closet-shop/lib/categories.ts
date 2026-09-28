import type { MaLetter } from "@/lib/ma";
import { TYPE_LABELS } from "@/lib/catalog";

export const TYPE_SLUGS: Record<MaLetter, string> = {
  A: "ao",
  Q: "quan",
  V: "vay",
  K: "ao-khoac",
  G: "giay",
  B: "tui",
  P: "phu-kien",
  H: "toc",
  J: "trang-suc",
  S: "set",
  O: "khac",
  D: "dam",
};

const SLUG_TO_TYPE = Object.fromEntries(
  (Object.entries(TYPE_SLUGS) as Array<[MaLetter, string]>).map(([type, slug]) => [
    slug,
    type,
  ]),
) as Record<string, MaLetter>;

export function categorySlug(type: MaLetter): string {
  return TYPE_SLUGS[type];
}

export function categoryFromSlug(slug: string): MaLetter | null {
  return SLUG_TO_TYPE[slug] ?? null;
}

export function categoryHref(type: MaLetter): string {
  return `/c/${categorySlug(type)}`;
}

export function categoryCopy(type: MaLetter): { label: string; singular: string } {
  const labels = TYPE_LABELS[type];
  return { label: labels.nav, singular: labels.en };
}

export function categoryAriaLabel(type: MaLetter): string {
  const labels = TYPE_LABELS[type];
  return `${labels.vn} · ${labels.nav}`;
}

/** Short Vietnamese names for the on-page filter chips. */
export function categoryFilterLabel(type: MaLetter): string {
  switch (type) {
    case "A":
      return "Áo";
    case "Q":
      return "Quần";
    case "V":
      return "Váy";
    case "D":
      return "Đầm";
    case "S":
      return "Set";
    case "K":
      return "Khoác";
    case "P":
      return "Phụ kiện";
    case "G":
      return TYPE_LABELS.G.vn;
    case "B":
      return TYPE_LABELS.B.vn;
    case "H":
      return TYPE_LABELS.H.vn;
    case "J":
      return TYPE_LABELS.J.vn;
    case "O":
      return TYPE_LABELS.O.vn;
    default: {
      const _exhaustive: never = type;
      return _exhaustive;
    }
  }
}

export function categoryTileSrc(type: MaLetter): string {
  return `/editorial/${categorySlug(type)}.jpg`;
}
