import { isOffLiveSell } from "@/lib/held-incomplete";
import type { MaLetter } from "@/lib/ma";

/** Looks listed on the home board. Held mãs stay off this list. */
export function homeLooks<T extends { ma: string }>(looks: T[]): T[] {
  return looks.filter((look) => !isOffLiveSell(look.ma));
}

/** Looks rendered in one shop category section. Same held-list filter as the home list. */
export function categoryGridLooks<T extends { ma: string; type: MaLetter }>(
  looks: T[],
  type: MaLetter,
): T[] {
  return homeLooks(looks).filter((look) => look.type === type);
}
