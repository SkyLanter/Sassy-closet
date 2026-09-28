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

/** Same English names as the top menu (`TYPE_LABELS.nav`). */
export function categoryFilterLabel(type: MaLetter): string {
  switch (type) {
    case "A":
      return TYPE_LABELS.A.nav;
    case "Q":
      return TYPE_LABELS.Q.nav;
    case "V":
      return TYPE_LABELS.V.nav;
    case "D":
      return TYPE_LABELS.D.nav;
    case "S":
      return TYPE_LABELS.S.nav;
    case "K":
      return TYPE_LABELS.K.nav;
    case "P":
      return TYPE_LABELS.P.nav;
    case "G":
      return TYPE_LABELS.G.nav;
    case "B":
      return TYPE_LABELS.B.nav;
    case "H":
      return TYPE_LABELS.H.nav;
    case "J":
      return TYPE_LABELS.J.nav;
    case "O":
      return TYPE_LABELS.O.nav;
    default: {
      const _exhaustive: never = type;
      return _exhaustive;
    }
  }
}

export function categoryTileSrc(type: MaLetter): string {
  return `/editorial/${categorySlug(type)}.jpg`;
}
