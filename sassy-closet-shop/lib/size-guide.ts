/**
 * Size text already stored on a shop look.
 * Returns those strings unchanged. Does not add letters, shoe sizes, or measurements.
 */
export function storedSizeText(sizes: readonly string[]): string[] {
  const text: string[] = [];
  for (const size of sizes) {
    if (typeof size !== "string") {
      continue;
    }
    const trimmed = size.trim();
    if (!trimmed) {
      continue;
    }
    text.push(trimmed);
  }
  return text;
}
