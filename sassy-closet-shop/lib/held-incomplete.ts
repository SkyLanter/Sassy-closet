/**
 * Incomplete Taobao mãs and the never-list. Loaded from data/held.json.
 * Public sell pages omit these mãs. This module does not write Blob.
 */
import held from "../../data/held.json";

export const HELD_INCOMPLETE_MAS: readonly string[] = held.heldIncomplete;

export const NEVER_LIST_MAS: readonly string[] = held.neverList;

const HELD_INCOMPLETE_SET: ReadonlySet<string> = new Set(
  HELD_INCOMPLETE_MAS.map((ma) => ma.toUpperCase()),
);

const NEVER_LIST_SET: ReadonlySet<string> = new Set(NEVER_LIST_MAS.map((ma) => ma.toUpperCase()));

export function isHeldIncompleteMa(ma: string): boolean {
  return HELD_INCOMPLETE_SET.has(ma.trim().toUpperCase());
}

/** True when data/held.json keeps this mã off the public sell catalog. */
export function isOffLiveSell(ma: string): boolean {
  const code = ma.trim().toUpperCase();
  return HELD_INCOMPLETE_SET.has(code) || NEVER_LIST_SET.has(code);
}
