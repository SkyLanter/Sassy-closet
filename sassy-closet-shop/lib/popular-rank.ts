import popularOrder from "@/data/popular-order.json";

/** Meta FB+IG equal rank-position weight (1/rank summed). Higher = more popular. */
const SCORE = new Map<string, number>(
  Object.entries((popularOrder as { scores: Record<string, number> }).scores ?? {}),
);

const ORDER = ((popularOrder as { order: string[] }).order ?? []).filter(Boolean);

export function popularScore(ma: string): number {
  return SCORE.get(ma) ?? 0;
}

/** Popular first (Meta equal FB/IG rank weight), then stable catalog order. */
export function sortByPopular<T extends { ma: string }>(products: T[]): T[] {
  if (ORDER.length === 0) {
    return products;
  }
  const index = new Map(ORDER.map((ma, i) => [ma, i]));
  return products
    .map((product, catalogIndex) => ({ product, catalogIndex }))
    .sort((left, right) => {
      const li = index.has(left.product.ma) ? (index.get(left.product.ma) as number) : ORDER.length;
      const ri = index.has(right.product.ma) ? (index.get(right.product.ma) as number) : ORDER.length;
      if (li !== ri) {
        return li - ri;
      }
      return left.catalogIndex - right.catalogIndex;
    })
    .map((row) => row.product);
}
