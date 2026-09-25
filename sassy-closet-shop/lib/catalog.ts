import { MA_LETTERS, type MaLetter } from "./ma";

export const TYPE_LABELS: Record<
  MaLetter,
  { vn: string; en: string; nav: string }
> = {
  A: { vn: "Áo", en: "Top", nav: "Tops" },
  Q: { vn: "Quần", en: "Pants", nav: "Bottoms" },
  V: { vn: "Váy", en: "Skirt", nav: "Skirts" },
  K: { vn: "Áo khoác", en: "Jacket", nav: "Jackets" },
  G: { vn: "Giày", en: "Shoes", nav: "Shoes" },
  B: { vn: "Túi", en: "Bag", nav: "Bags" },
  P: { vn: "Phụ kiện", en: "Accessory", nav: "Accessories" },
  H: { vn: "Tóc", en: "Hair", nav: "Hair" },
  J: { vn: "Trang sức", en: "Jewelry", nav: "Jewelry" },
  S: { vn: "Set đồ", en: "Set", nav: "Sets" },
  O: { vn: "Khác", en: "Other", nav: "Other" },
  D: { vn: "Đầm", en: "Dress", nav: "Dresses" },
};

export function typeLabel(type: MaLetter): { vn: string; en: string; nav: string } {
  return TYPE_LABELS[type];
}

export function letterPickerOptions(): Array<{ letter: MaLetter; label: string }> {
  return MA_LETTERS.map((letter) => ({
    letter,
    label: `${letter} · ${TYPE_LABELS[letter].nav}`,
  }));
}
