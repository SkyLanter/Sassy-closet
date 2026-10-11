/**
 * Incomplete Taobao mãs. Dataset and admin only.
 * The mãs are loaded from data/held.json. This module does not write the
 * sell catalog, change a price, or publish a mã.
 */
import held from "../../data/held.json";

export const HELD_INCOMPLETE_MAS: readonly string[] = held.heldIncomplete;

export const NEVER_LIST_MAS: readonly string[] = held.neverList;

export type HeldIncompleteMa = (typeof HELD_INCOMPLETE_MAS)[number];

const HELD_INCOMPLETE_SET: ReadonlySet<string> = new Set(
  HELD_INCOMPLETE_MAS.map((ma) => ma.toUpperCase()),
);

export function isHeldIncompleteMa(ma: string): ma is HeldIncompleteMa {
  return HELD_INCOMPLETE_SET.has(ma.trim().toUpperCase());
}
