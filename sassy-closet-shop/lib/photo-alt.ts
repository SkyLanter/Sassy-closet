/** Alt from the garment title, the mã, and a catalog color when one is known. */
export function lookPhotoAlt(input: {
  title: string;
  ma: string;
  color?: string | null;
  index?: number;
}): string {
  const title = input.title.trim();
  const parts: string[] = [];
  if (title && title.toUpperCase() !== input.ma.toUpperCase()) {
    parts.push(title);
  }
  parts.push(`Mã ${input.ma}`);
  const color = input.color?.trim();
  if (color) {
    parts.push(color);
  }
  if (input.index && input.index > 0) {
    parts.push(`photo ${input.index}`);
  }
  return parts.join(", ");
}
