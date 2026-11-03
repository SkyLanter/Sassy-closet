import Link from "next/link";
import { categoryAriaLabel, categoryCopy, categoryHref } from "@/lib/categories";
import type { MaLetter } from "@/lib/ma";

export function CategorySuggestChips({
  types,
  className = "",
}: {
  types: MaLetter[];
  className?: string;
}) {
  if (types.length === 0) {
    return null;
  }

  return (
    <div className={className} data-testid="category-suggest-chips">
      <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.16em] text-muted" translate="no">
        Danh mục · Categories
      </p>
      <div className="flex flex-wrap justify-center gap-2">
        {types.map((type) => {
          const labels = categoryCopy(type);
          return (
            <Link
              key={type}
              href={categoryHref(type)}
              aria-label={categoryAriaLabel(type)}
              translate="no"
              className="sc-chip-face inline-flex min-h-11 touch-manipulation select-none items-center rounded-full border border-line bg-transparent px-3 text-[11px] font-medium uppercase tracking-[0.16em] text-ink"
            >
              {labels.label}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
