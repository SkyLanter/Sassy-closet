import type { Fulfillment } from "@/lib/fulfillment";
import type { Product, ProductStatus } from "@/lib/types";

export const HOLD_PRICE_LABEL = "Inbox for price";
export const HOLD_ASK_LABEL = "Nhắn tin hỏi giá";
export const HOLD_PRICE_LINE = "Inbox for price · Nhắn tin hỏi giá";
export const MESSAGE_ORDER = "Message to order";
export const MESSAGE_BUY = "Message to buy";
export const SHIP_QUOTE = "Ship quoted in chat · no flat rate";
export const SPOT_PRESALE_EN = "Spot / pre-sale in chat";
export const SPOT_PRESALE_VN = "Sẵn / đặt trước — chốt khi inbox";
export const SPOT_PRESALE_LINE = `${SPOT_PRESALE_EN} · ${SPOT_PRESALE_VN}`;
export const HOLD_LOOKBOOK_EN = "Character tumbler.";
export const HOLD_LOOKBOOK_VN = "Bình nhân vật.";

/** Extra mãs with no real garment copy stay blank — never invent a listed/unique blurb. */
export function listedLookDescriptionEn(_ma: string): string {
  return "";
}

export function listedLookDescriptionVn(_ma: string): string {
  return "";
}

export function holdPhotoCheckDescriptionEn(_kind: string): string {
  return "";
}

export function holdPhotoCheckDescriptionVn(_kindVn: string): string {
  return "";
}
export {
  DEST_LINE,
  FULFILL_LINE,
  FULFILL_LINE_SHORT,
  FULFILL_LINE_VN,
  PAY_LINE,
} from "@/lib/trust-copy";

export function holdAskCta(ma?: string): string {
  return ma ? `${HOLD_ASK_LABEL} ${ma}` : HOLD_ASK_LABEL;
}

export function orderCta(status: ProductStatus, ma?: string): string {
  switch (status) {
    case "hold":
    case "available":
    case "sold":
      return ma ? `${MESSAGE_BUY} ${ma}` : MESSAGE_BUY;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

export function buyHint(fulfillment: Fulfillment): string {
  switch (fulfillment) {
    case "on_hand":
    case "dropship":
      return MESSAGE_BUY;
    default: {
      const _exhaustive: never = fulfillment;
      return _exhaustive;
    }
  }
}

/** Card / grid line under the price. Kelly Ying look lock: available = Message to buy. */
export function cardBuyHint(product: Product): string {
  switch (product.status) {
    case "hold":
    case "available":
    case "sold":
      return MESSAGE_BUY;
    default: {
      const _exhaustive: never = product.status;
      return _exhaustive;
    }
  }
}

export function statusNote(product: Product): string {
  switch (product.status) {
    case "hold":
    case "available":
      return "";
    case "sold":
      return "Sold.";
    default: {
      const _exhaustive: never = product.status;
      return _exhaustive;
    }
  }
}
