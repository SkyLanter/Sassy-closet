/**
 * Incomplete Taobao mãs. Dataset and admin only.
 * Standing never-publish set. This module does not write the sell catalog,
 * change a price, or publish a mã.
 */
export const HELD_INCOMPLETE_MAS = ["S14", "A24", "A25", "S15", "A26", "K02", "K03", "K04", "K05", "V04"] as const;

export type HeldIncompleteMa = (typeof HELD_INCOMPLETE_MAS)[number];

/** Permanently unlisted. Not part of the held incomplete set, and not a price. */
export const UNLISTED_MAS = ["Q02"] as const;

const HELD_INCOMPLETE_SET: ReadonlySet<string> = new Set(HELD_INCOMPLETE_MAS);
const UNLISTED_SET: ReadonlySet<string> = new Set(UNLISTED_MAS);

export function isHeldIncompleteMa(ma: string): ma is HeldIncompleteMa {
  return HELD_INCOMPLETE_SET.has(ma.trim().toUpperCase());
}

export function isUnlistedMa(ma: string): boolean {
  return UNLISTED_SET.has(ma.trim().toUpperCase());
}
