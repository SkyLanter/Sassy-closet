/**
 * Incomplete Taobao mãs. Dataset and admin only.
 * Standing never-publish set. This module does not write the sell catalog,
 * change a price, or publish a mã.
 */
export const HELD_INCOMPLETE_MAS = ["S14", "A24", "A25", "S15", "A26", "K02", "K03", "K04", "K05", "V04", "K06"] as const;

export type HeldIncompleteMa = (typeof HELD_INCOMPLETE_MAS)[number];

const HELD_INCOMPLETE_SET: ReadonlySet<string> = new Set(HELD_INCOMPLETE_MAS);

export function isHeldIncompleteMa(ma: string): ma is HeldIncompleteMa {
  return HELD_INCOMPLETE_SET.has(ma.trim().toUpperCase());
}
