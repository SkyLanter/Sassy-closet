import { kindLabel } from "./kinds";
import type { Submission } from "./types";

const BLURB_VI: Record<string, string> = {
  A: "Chiếc áo cưng xỉu 💕",
  Q: "Chiếc quần cưng xỉu 💕",
  V: "Chiếc váy cưng xỉu 💕",
  D: "Chiếc đầm cưng xỉu 💕",
  K: "Áo khoác cưng xỉu 💕",
  G: "Đôi giày cưng xỉu 💕",
  B: "Chiếc túi cưng xỉu 💕",
  P: "Món nhỏ xinh xỉu 💕",
  H: "Món tóc xinh xỉu 💕",
  J: "Món trang sức xinh xỉu 💕",
  S: "Set đồ cưng xỉu 💕",
  O: "Món cưng xỉu 💕",
};

const FOOTER = "Inbox mã để lấy nha 💕 Local cash/Zelle. Ship toàn US.";

export function captionStarter(ma: string): string {
  return normalizeCaptionMa(ma);
}

export function kindColorsLine(input: {
  kind: string;
  color: string;
  color_note?: string;
}): string {
  const kind = kindLabel(input.kind);
  const color = input.color.trim();
  const note = (input.color_note ?? "").trim();
  if (color && note) return `${kind} · ${color} · ${note}`;
  if (color) return `${kind} · ${color}`;
  if (note) return `${kind} · ${note}`;
  return kind;
}

export function buildCaptionVi(item: Pick<Submission, "ma" | "kind" | "size" | "color" | "color_note" | "sell_usd" | "sell_cny" | "sell_currency" | "price" | "blurb">): string {
  const blurb = item.blurb.trim() || BLURB_VI[item.kind] || BLURB_VI.A;
  const size = item.size.trim() ? `Size ${item.size.trim()}` : "";
  const color = colorLine(item.color, item.color_note);
  const price = priceLine(item);
  return [item.ma, blurb, size, color, price, FOOTER].filter(Boolean).join("\n");
}

export function editDeepLink(origin: string, ma: string): string {
  const url = new URL(origin);
  url.pathname = "/";
  url.search = "";
  url.hash = "";
  url.searchParams.set("ma", normalizeCaptionMa(ma));
  return url.toString();
}

function colorLine(color: string, note: string): string {
  const c = color.trim();
  const n = note.trim();
  if (c && n) return `Màu ${c} · ${n}`;
  if (c) return `Màu ${c}`;
  if (n) return `Màu ${n}`;
  return "";
}

function priceLine(item: Pick<Submission, "sell_usd" | "sell_cny" | "sell_currency" | "price">): string {
  if ((item.sell_currency ?? "").toUpperCase() === "CNY" && item.sell_cny) {
    return `¥${item.sell_cny}`;
  }
  if (item.sell_usd) return `$${item.sell_usd}`;
  if (item.sell_cny) return `¥${item.sell_cny}`;
  if (item.price) return `$${item.price}`;
  return "";
}

function normalizeCaptionMa(ma: string): string {
  return ma.trim().toUpperCase();
}
