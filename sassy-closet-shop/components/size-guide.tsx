import { storedSizeText } from "@/lib/size-guide";

/** Lists the size text already on this look. Hidden when the row has none. */
export function SizeGuide({ sizes }: { sizes: readonly string[] }) {
  const lines = storedSizeText(sizes);
  if (lines.length === 0) {
    return null;
  }

  return (
    <section className="mt-4" data-testid="size-guide" aria-labelledby="size-guide-label">
      <p
        id="size-guide-label"
        className="mb-2 text-[11px] uppercase tracking-[0.16em] text-muted"
        translate="no"
      >
        Bảng size · Size guide
      </p>
      <p
        className="text-[13px] font-medium tracking-[0.12em] text-ink"
        translate="no"
        data-testid="size-guide-text"
      >
        {lines.join(" ")}
      </p>
    </section>
  );
}
