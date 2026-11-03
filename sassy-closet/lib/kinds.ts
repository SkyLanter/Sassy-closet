export const KIND_CODES = ["A", "Q", "V", "D", "K", "G", "B", "P", "H", "J", "S", "O"] as const;

export type KindCode = (typeof KIND_CODES)[number];

export type Kind = {
  code: KindCode;
  label: string;
  hint: string;
};

export const KINDS: Kind[] = [
  { code: "A", label: "Áo", hint: "A" },
  { code: "Q", label: "Quần", hint: "Q" },
  { code: "V", label: "Váy", hint: "V" },
  { code: "D", label: "Đầm / Dress", hint: "D" },
  { code: "K", label: "Áo khoác", hint: "K" },
  { code: "G", label: "Giày / Cao gót", hint: "G" },
  { code: "B", label: "Túi", hint: "B" },
  { code: "P", label: "Phụ kiện", hint: "P" },
  { code: "H", label: "Phụ kiện tóc / Hair accessories", hint: "H" },
  { code: "J", label: "Trang sức / Jewelry", hint: "J" },
  { code: "S", label: "Set đồ", hint: "S" },
  { code: "O", label: "Khác / Other", hint: "O" },
];

export const CLOTHING_SIZES = ["2XS", "XS", "S", "M", "L", "XL", "2XL"] as const;
export const SHOE_SIZES = ["35", "36", "37", "38", "39", "40", "41"] as const;
/** Clothing Asia sizes. Prefer `sizesForKind` so giày (G) stays on 35–41. */
export const SIZES = CLOTHING_SIZES;

export type ColorChip = {
  code: string;
  vi: string;
};

export const COLORS: ColorChip[] = [
  { code: "den", vi: "Đen" },
  { code: "trang", vi: "Trắng" },
  { code: "kem", vi: "Kem" },
  { code: "be", vi: "Be" },
  { code: "hong", vi: "Hồng" },
  { code: "do", vi: "Đỏ" },
  { code: "xanh", vi: "Xanh" },
  { code: "nau", vi: "Nâu" },
  { code: "xam", vi: "Xám" },
  { code: "bac", vi: "Bạc" },
  { code: "vang", vi: "Vàng" },
  { code: "cam", vi: "Cam" },
  { code: "tim", vi: "Tím" },
  { code: "xanhduong", vi: "Xanh dương" },
  { code: "xanhla", vi: "Xanh lá" },
  { code: "hongdam", vi: "Hồng đậm" },
  { code: "nude", vi: "Nude" },
  { code: "naudam", vi: "Nâu đậm" },
  { code: "trangnga", vi: "Trắng ngà" },
  { code: "dodo", vi: "Đỏ đô" },
  { code: "vangchanh", vi: "Vàng chanh" },
  { code: "mint", vi: "Xanh mint" },
  { code: "pastel", vi: "Pastel" },
  { code: "anhkim", vi: "Ánh kim" },
  { code: "caro", vi: "Caro" },
  { code: "hoa", vi: "Hoa" },
  { code: "khac", vi: "Khác" },
];

export type SizeScale = "shoe" | "clothing";

export type IntakeCatalogKind = {
  code: KindCode;
  label: string;
  hint: string;
  sizes: string[];
};

export type IntakeCatalog = {
  kinds: IntakeCatalogKind[];
};

export function isKindCode(value: string): value is KindCode {
  return (KIND_CODES as readonly string[]).includes(value);
}

export function kindLabel(code: string): string {
  const found = KINDS.find((k) => k.code === code);
  return found?.label ?? code;
}

export function sizeScaleForKind(kind: KindCode): SizeScale {
  switch (kind) {
    case "G":
      return "shoe";
    case "A":
    case "Q":
    case "V":
    case "D":
    case "K":
    case "B":
    case "P":
    case "H":
    case "J":
    case "S":
    case "O":
      return "clothing";
    default: {
      const _never: never = kind;
      return assertNever(_never, `Unknown kind ${String(kind)}`);
    }
  }
}

export function sizesForKind(kind: KindCode): readonly string[] {
  return sizeScaleForKind(kind) === "shoe" ? SHOE_SIZES : CLOTHING_SIZES;
}

export function sizeOptionsLine(kind: KindCode): string {
  return sizesForKind(kind).join(" ");
}

export function keepSizesForKind(selected: string[], kind: KindCode): string[] {
  const allowed = new Set<string>(sizesForKind(kind));
  return selected.filter((size) => allowed.has(size));
}

export function intakeCatalog(): IntakeCatalog {
  return {
    kinds: KINDS.map((kind) => ({
      code: kind.code,
      label: kind.label,
      hint: kind.hint,
      sizes: [...sizesForKind(kind.code)],
    })),
  };
}

export function assertNever(value: never, message: string): never {
  throw new Error(message);
}
