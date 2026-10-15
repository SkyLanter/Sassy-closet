import { isOffLiveSell } from "@/lib/held-incomplete";
import type { MaLetter } from "@/lib/ma";

/** Looks rendered in one shop category section. Held mãs stay off this grid. */
export function categoryGridLooks<T extends { ma: string; type: MaLetter }>(
  looks: T[],
  type: MaLetter,
): T[] {
  return looks.filter((look) => look.type === type && !isOffLiveSell(look.ma));
}
