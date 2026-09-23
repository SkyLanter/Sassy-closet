import { isValidMa } from "@/lib/ma";
import type { Product } from "@/lib/types";

export const PUBLIC_FORBIDDEN_PHRASES = [
  "Square",
  "ADMIN_PASSWORD",
  "Facebook Send",
  "FB Send",
  "Thang Tien Huynh",
  "Shop now",
  "Add to cart",
] as const;

/** Customer-visible stock / availability voice. Admin may still say Hold internally. */
const CUSTOMER_STOCK_VOICE: Array<[string, RegExp]> = [
  ["Hold", /\bHold\b/],
  ["Available", /\bAvailable\b/],
  ["Status:", /Status:\s/],
  ["on hand", /\bon hand\b/i],
  ["on-hand", /on-hand/i],
  ["đang có", /đang có/i],
  ["in-stock", /in-stock/i],
  ["In stock", /\bIn stock\b/i],
  ["Tạm giữ", /Tạm giữ/],
];

/** How we buy / stock / source — never print this on the customer shop. */
const CUSTOMER_OPS_VOICE: Array<[string, RegExp]> = [
  ["Taobao", /Taobao/i],
  ["Zelle", /\bZelle\b/],
  ["dropship", /dropship/i],
  ["CNY", /\bCNY\b/],
  ["source_link", /source_link/i],
  ["we order", /we order/i],
  ["photo-check", /photo-check/i],
  ["no cart", /no cart/i],
  ["flat rate", /flat rate/i],
  ["Message-first", /Message-first/],
  ["Asia size", /Asia size/i],
  ["size Á châu", /size Á châu/i],
  ["Nhắn tin hỏi giá", /Nhắn tin hỏi giá/],
  ["sourced after", /sourced after/i],
  ["inbox màu", /inbox màu/i],
];

/** Invented boutique filler — never print on the customer shop. */
const CUSTOMER_FILLER_VOICE: Array<[string, RegExp]> = [
  ["unique pieces", /unique pieces/i],
  ["unique piece", /unique piece/i],
  ["unique top", /unique top/i],
  ["curated", /curated/i],
  ["A listed", /A listed /i],
  ["độc bản", /độc bản/i],
  ["not reserved", /not reserved/i],
];

export function customerStockVoiceHit(text: string): string | null {
  for (const [label, pattern] of CUSTOMER_STOCK_VOICE) {
    if (pattern.test(text)) {
      return label;
    }
  }
  return null;
}

export function customerFillerVoiceHit(text: string): string | null {
  for (const [label, pattern] of CUSTOMER_FILLER_VOICE) {
    if (pattern.test(text)) {
      return label;
    }
  }
  return null;
}

export function customerOpsVoiceHit(text: string): string | null {
  const stock = customerStockVoiceHit(text);
  if (stock) {
    return stock;
  }
  for (const [label, pattern] of CUSTOMER_OPS_VOICE) {
    if (pattern.test(text)) {
      return label;
    }
  }
  const filler = customerFillerVoiceHit(text);
  if (filler) {
    return filler;
  }
  return null;
}

export type PublicSafety = {
  ok: boolean;
  inventedMas: string[];
};

export function catalogPublicSafety(products: Product[]): PublicSafety {
  const inventedMas = products
    .map((product) => product.ma)
    .filter((ma) => !isValidMa(ma));
  return {
    ok: inventedMas.length === 0,
    inventedMas,
  };
}
