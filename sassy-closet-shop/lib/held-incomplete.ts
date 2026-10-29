/**
 * Incomplete Taobao mãs and the never-list. Loaded from data/held.json.
 * Public sell pages omit these mãs. This module does not write Blob.
 */
import held from "../../data/held.json";
import { canonicalMaSpelling } from "./ma";

export const HELD_INCOMPLETE_MAS: readonly string[] = held.heldIncomplete;

export const NEVER_LIST_MAS: readonly string[] = held.neverList;

/** One helper: same canonical spelling as lib/ma (kept for piece-146 callers). */
export const canonicalHeldKey = canonicalMaSpelling;

const HELD_INCOMPLETE_SET: ReadonlySet<string> = new Set(
  HELD_INCOMPLETE_MAS.map(canonicalMaSpelling),
);

const NEVER_LIST_SET: ReadonlySet<string> = new Set(NEVER_LIST_MAS.map(canonicalMaSpelling));

export function isHeldIncompleteMa(ma: string): boolean {
  return HELD_INCOMPLETE_SET.has(canonicalMaSpelling(ma));
}

/** True when data/held.json keeps this mã off the public sell catalog. */
export function isOffLiveSell(ma: string): boolean {
  const code = canonicalMaSpelling(ma);
  return HELD_INCOMPLETE_SET.has(code) || NEVER_LIST_SET.has(code);
}
