import { messengerHref } from "@/lib/messenger";

/**
 * Product Message only. Header and footer stay a plain m.me chat.
 * Missing size or color is left out. Nothing is invented.
 */
export function messengerAskSentence(
  ma: string,
  size: string | null,
  color: string | null,
): string {
  const code = ma.trim();
  let sentence = `Chị ơi, còn ${code}`;
  const sizeLabel = size?.trim();
  const colorLabel = color?.trim();
  if (sizeLabel) {
    sentence += ` size ${sizeLabel}`;
  }
  if (colorLabel) {
    sentence += ` màu ${colorLabel}`;
  }
  return `${sentence} không ạ?`;
}

/** Same m.me thread as today, opened directly, with the ask in the text field. */
export function messengerAskHref(
  pageUrl: string,
  ma: string,
  size: string | null,
  color: string | null,
): string {
  return messengerTextHref(pageUrl, messengerAskSentence(ma, size, color));
}

/**
 * Size help only. Blanks stay blanks — nothing is invented.
 * A selected size or color is appended, the same way the buy ask names them.
 */
export function messengerSizeAskSentence(
  ma: string,
  size: string | null,
  color: string | null,
): string {
  const code = ma.trim();
  let sentence = `Chị ơi, em cao ___ cm, nặng ___ kg. ${code} em nên lấy size nào ạ?`;
  const sizeLabel = size?.trim();
  const colorLabel = color?.trim();
  if (sizeLabel) {
    sentence += ` Size ${sizeLabel}.`;
  }
  if (colorLabel) {
    sentence += ` Màu ${colorLabel}.`;
  }
  return sentence;
}

export function messengerSizeAskHref(
  pageUrl: string,
  ma: string,
  size: string | null,
  color: string | null,
): string {
  return messengerTextHref(pageUrl, messengerSizeAskSentence(ma, size, color));
}

function messengerTextHref(pageUrl: string, text: string): string {
  const base = messengerHref(pageUrl);
  if (!base) {
    return "";
  }
  const url = new URL(base);
  url.searchParams.set("text", text);
  return url.toString();
}
