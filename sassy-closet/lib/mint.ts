import { NEVER_LIST_MAS } from "./held-incomplete";
import { KIND_CODES, isKindCode, type KindCode } from "./kinds";

export type ParsedMa = {
  kind: KindCode;
  n: number;
};

export const MAX_MA_NUMBER = 999;

const MA_RE = new RegExp(`^([${KIND_CODES.join("")}])(\\d{2,})$`, "i");

export function parseHubMa(raw: string): ParsedMa | null {
  const match = raw.trim().toUpperCase().match(MA_RE);
  if (!match) return null;
  const kind = match[1].toUpperCase();
  if (!isKindCode(kind)) return null;
  const n = Number(match[2]);
  if (!Number.isInteger(n) || n < 1 || n > MAX_MA_NUMBER) return null;
  return { kind, n };
}

export function formatMa(kind: KindCode, n: number): string {
  const digits = n < 100 ? String(n).padStart(2, "0") : String(n);
  return `${kind}${digits}`;
}

/**
 * Canonical mã spelling: trim, upper-case, two-digit padding ("s6" / "S006" -> "S06"), so no
 * spelling dodges S06 / held. Must agree with sassy-closet-shop/lib/ma.ts canonicalMaSpelling and
 * scripts/held_policy.py norm_ma (pinned by scripts/testdata/ma-normalization-vectors.json).
 */
export function normalizeMa(raw: string): string {
  const code = raw.trim().toUpperCase();
  const short = code.match(/^([A-Z])(\d+)$/);
  const padded = short ? `${short[1]}${String(Number(short[2])).padStart(2, "0")}` : code;
  const parsed = parseHubMa(padded);
  return parsed ? formatMa(parsed.kind, parsed.n) : padded;
}

/** Next free number. Skips never-list mãs and numbers already in `existing`. */
export function nextMa(
  kind: KindCode,
  existing: string[],
  blocked: readonly string[] = [],
): string {
  const taken = numbersForKind(kind, existing);
  let max = 0;
  for (const n of taken) {
    if (n > max) max = n;
  }
  const skipped = numbersForKind(kind, [...NEVER_LIST_MAS, ...blocked]);
  let n = max + 1;
  while (taken.has(n) || skipped.has(n)) n += 1;
  if (n > MAX_MA_NUMBER) {
    // Past 999 parseHubMa rejects the code, so it would be invisible to the
    // next call and minted again. Never reuse a lower gap: retired/old mãs
    // must not be reissued (shop rule; piece 126 never fills gaps either).
    throw new Error(`No free mã left for kind ${kind} (past ${MAX_MA_NUMBER}; gaps are never reused)`);
  }
  return formatMa(kind, n);
}

function numbersForKind(kind: KindCode, mas: readonly string[]): Set<number> {
  const numbers = new Set<number>();
  for (const ma of mas) {
    // Canonical first so a short "K3" still counts as taken (never reuse a mã).
    const parsed = parseHubMa(normalizeMa(ma));
    if (parsed && parsed.kind === kind) numbers.add(parsed.n);
  }
  return numbers;
}

export function maExists(existing: string[], ma: string, except?: string): boolean {
  const target = normalizeMa(ma);
  const skip = except ? normalizeMa(except) : "";
  return existing.some((item) => {
    const value = normalizeMa(item);
    return value === target && value !== skip;
  });
}
