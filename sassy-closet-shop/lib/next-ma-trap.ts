/** Official #29 invent-mã tiles crawled on stale Vercel. Not shop stock. */
export const INVENTED_NEXT_MAS = [
  "A03",
  "Q01",
  "V01",
  "K02",
  "G01",
  "B01",
  "P06",
  "H02",
  "J01",
  "S02",
  "O01",
  "D01",
] as const;

export type InventedNextMa = (typeof INVENTED_NEXT_MAS)[number];

/** Visible label Official treated as a published SKU tile. */
export function nextMaTrapLabel(ma: string): string {
  return `Add ${ma}`;
}

export function nextMaTrapLabels(): string[] {
  return INVENTED_NEXT_MAS.map((ma) => nextMaTrapLabel(ma));
}

export function htmlHasNextMaTrap(text: string): string[] {
  return nextMaTrapLabels().filter((label) => text.includes(label));
}
