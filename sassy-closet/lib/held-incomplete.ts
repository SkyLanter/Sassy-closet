/**
 * Incomplete Taobao mãs. Dataset and admin only.
 * The mãs are loaded from data/held.json. This module does not write the
 * sell catalog, change a price, or publish a mã.
 */
import held from "../../data/held.json";

export const HELD_INCOMPLETE_MAS: readonly string[] = held.heldIncomplete;

export const NEVER_LIST_MAS: readonly string[] = held.neverList;

export type HeldIncompleteMa = (typeof HELD_INCOMPLETE_MAS)[number];

/** Canonical key: trim, upper-case, drop zero padding to two digits ("A024" -> "A24"). Local to avoid an import cycle with mint.ts. */
export function canonicalHeldKey(ma: string): string {
  const code = ma.trim().toUpperCase();
  const match = code.match(/^([A-Z])(\d+)$/);
  if (!match) return code;
  return `${match[1]}${String(Number(match[2])).padStart(2, "0")}`;
}

const HELD_INCOMPLETE_SET: ReadonlySet<string> = new Set(
  HELD_INCOMPLETE_MAS.map(canonicalHeldKey),
);

export function isHeldIncompleteMa(ma: string): ma is HeldIncompleteMa {
  return HELD_INCOMPLETE_SET.has(canonicalHeldKey(ma));
}
