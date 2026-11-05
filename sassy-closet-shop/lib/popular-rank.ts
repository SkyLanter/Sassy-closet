import popularOrder from "@/data/popular-order.json";
import { canonicalMaSpelling } from "@/lib/ma";

/** Meta FB+IG equal rank-position weight (1/rank summed). Higher = more popular. */
const SCORE = new Map<string, number>();
for (const [ma, score] of Object.entries(
  (popularOrder as { scores: Record<string, number> }).scores ?? {},
)) {
  const code = canonicalMaSpelling(ma);
  if (!SCORE.has(code)) SCORE.set(code, score);
}

const ORDER = ((popularOrder as { order: string[] }).order ?? [])
  .filter(Boolean)
  .map((ma) => canonicalMaSpelling(ma));

export function popularScore(ma: string): number {
  return SCORE.get(canonicalMaSpelling(ma)) ?? 0;
}

/** Popular first (Meta equal FB/IG rank weight), then stable catalog order. */
export function sortByPopular<T extends { ma: string }>(products: T[]): T[] {
  if (ORDER.length === 0) {
    return products;
  }
  const index = new Map<string, number>();
  ORDER.forEach((ma, i) => {
    if (!index.has(ma)) index.set(ma, i);
  });
  return products
    .map((product, catalogIndex) => ({ product, catalogIndex }))
    .sort((left, right) => {
      const leftKey = canonicalMaSpelling(left.product.ma);
      const rightKey = canonicalMaSpelling(right.product.ma);
      const li = index.has(leftKey) ? (index.get(leftKey) as number) : ORDER.length;
      const ri = index.has(rightKey) ? (index.get(rightKey) as number) : ORDER.length;
      if (li !== ri) {
        return li - ri;
      }
      return left.catalogIndex - right.catalogIndex;
    })
    .map((row) => row.product);
}
