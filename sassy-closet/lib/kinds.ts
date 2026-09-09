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
  { code: "G", label: "Giày", hint: "G" },
  { code: "B", label: "Túi", hint: "B" },
  { code: "H", label: "Tóc", hint: "H" },
  { code: "J", label: "Trang sức", hint: "J" },
  { code: "P", label: "Phụ kiện", hint: "P" },
  { code: "S", label: "Set đồ", hint: "S" },
  { code: "O", label: "Khác / Other", hint: "O" },
];

export const SIZES = ["2XS", "XS", "S", "M", "L", "XL", "2XL"] as const;

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

export function isKindCode(value: string): value is KindCode {
  return (KIND_CODES as readonly string[]).includes(value);
}

export function kindLabel(code: string): string {
  const found = KINDS.find((k) => k.code === code);
  return found?.label ?? code;
}

export function assertNever(value: never, message: string): never {
  throw new Error(message);
}
