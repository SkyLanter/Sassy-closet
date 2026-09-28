import { createHash, timingSafeEqual } from "node:crypto";

/** Shared with the intake app. Send this header on POST /api/admin/revalidate. */
export const SHOP_REVALIDATE_HEADER = "x-shop-revalidate-secret";

function digest(value: string): Buffer {
  return createHash("sha256").update(value, "utf8").digest();
}

/** Fail closed when the env is unset. Digests are equal length, then timingSafeEqual. */
export function revalidateSecretMatches(presented: string | null): boolean {
  const expected = process.env.SHOP_REVALIDATE_SECRET?.trim() ?? "";
  if (!expected || presented === null || presented.length === 0) {
    return false;
  }
  return timingSafeEqual(digest(presented), digest(expected));
}

export function revalidateRequestAuthorized(request: Request): boolean {
  return revalidateSecretMatches(request.headers.get(SHOP_REVALIDATE_HEADER));
}
