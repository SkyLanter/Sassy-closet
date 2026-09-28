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
  const base = messengerHref(pageUrl);
  if (!base) {
    return "";
  }
  const url = new URL(base);
  url.searchParams.set("text", messengerAskSentence(ma, size, color));
  return url.toString();
}
