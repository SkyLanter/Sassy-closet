import { categoryCopy } from "@/lib/categories";
import type { MaLetter } from "@/lib/ma";

export const HOME_TITLE = "Sassy Closet";
export const HOME_OG_TITLE = "Sassy Closet";
export const HOME_DESCRIPTION = "Sassy Closet. Message on Messenger.";

export const FULFILL_LINE = "Message on Messenger.";
export const FULFILL_LINE_SHORT = "Message on Messenger";
export const FULFILL_LINE_VN = "Nhắn tin trên Messenger.";

export const PAY_LINE = "Message on Messenger.";
export const PAY_LINE_VN = "Nhắn tin trên Messenger.";
export const DEST_LINE = "Message on Messenger.";
export const DEST_LINE_VN = "Nhắn tin trên Messenger.";

export const DROPSHIP_RAIL = "Message on Messenger.";
export const DROPSHIP_SPINE = "Message on Messenger";
export const HOLD_NOT_RESERVED = "Inbox for price.";
export const HOLD_NOT_RESERVED_VN = "Inbox hỏi giá.";
export const TB_ORDER_LINE = "Message on Messenger.";
export const TB_ORDER_LINE_VN = "Nhắn tin trên Messenger.";
export const DUTY_CHAT_LINE = "Message on Messenger.";
export const DUTY_CHAT_LINE_VN = "Nhắn tin trên Messenger.";

export const HOW_TO_BUY_LINE = "Message on Messenger.";
export const HOW_TO_BUY_LINE_VN = "Nhắn tin trên Messenger.";

export const HOW_TO_BUY_TITLE = "Message";
export const HOW_TO_BUY_DESCRIPTION = "Message on Messenger to buy.";
export const MEETUP_SHIP_TITLE = "Message";
export const MEETUP_SHIP_DESCRIPTION = "Message on Messenger to buy.";

/** Official #30 §9.2 — h-8 bar, ≤22 characters, no how-to paragraph. */
export const ANNOUNCEMENT_CHAR_BUDGET = 22;
export const ANNOUNCE_A0 = "Sassy Closet";
export const ANNOUNCEMENT_LINES = [ANNOUNCE_A0] as const;

const LEGACY_ANNOUNCEMENT_JOINS = new Set([
  "Facebook livestream|Zelle · Message on Messenger|Nhắn tin hỏi giá · Message to buy",
  "Facebook livestream|Zelle · Message on Messenger|Nhắn tin hỏi giá · Message to order",
  "Facebook livestream|Meetup or US-quote ship|Message · Zelle after confirm",
  "Facebook livestream|Meetup or US-quote ship",
  "Facebook livestream|Inbox · Zelle · US",
  "Sassy Closet|A small closet",
]);

export function isLegacyAnnouncement(lines: string[]): boolean {
  if (LEGACY_ANNOUNCEMENT_JOINS.has(lines.join("|"))) {
    return true;
  }
  return lines.some((line) =>
    /Zelle|Taobao|livestream|Nhắn tin hỏi giá|Message to buy|Inbox ·|A small closet|curated|Unique pieces/i.test(
      line,
    ),
  );
}

export type HowToBuyStage = "Message" | "Confirm" | "Zelle" | "Order";

export type HowToBuyStep = {
  stage: HowToBuyStage;
  en: string;
  vn: string;
};

export function howToBuySteps(ma?: string): HowToBuyStep[] {
  const piece = ma ? `${ma}` : "the mã";
  return [
    {
      stage: "Message",
      en: `Message ${piece} on Messenger.`,
      vn: ma ? `Nhắn tin ${ma} trên Messenger.` : "Nhắn tin mã trên Messenger.",
    },
    {
      stage: "Confirm",
      en: "Message on Messenger.",
      vn: "Nhắn tin trên Messenger.",
    },
    {
      stage: "Zelle",
      en: "Message on Messenger.",
      vn: "Nhắn tin trên Messenger.",
    },
    {
      stage: "Order",
      en: "Message on Messenger.",
      vn: "Nhắn tin trên Messenger.",
    },
  ];
}

export function categoryShareDescription(type: MaLetter): string {
  const { label } = categoryCopy(type);
  switch (type) {
    case "A":
    case "Q":
    case "V":
    case "K":
    case "G":
    case "B":
    case "P":
    case "H":
    case "J":
    case "S":
    case "O":
    case "D":
      return `${label} · Sassy Closet`;
    default: {
      const _exhaustive: never = type;
      return _exhaustive;
    }
  }
}

export function productShareTitle(product: { ma: string; titleEn: string }): string {
  return `${product.ma} · ${product.titleEn}`;
}

export function productShareDescription(product: {
  ma: string;
  titleEn: string;
  descriptionEn: string;
}): string {
  const body = product.descriptionEn.trim() || product.titleEn.trim();
  return `${product.ma} · ${body}`;
}

export function productOgAlt(product: { ma: string; titleEn: string }): string {
  return `${product.ma} ${product.titleEn.toLowerCase()} — Sassy Closet`;
}
