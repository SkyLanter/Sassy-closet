import { NEVER_LIST_MAS } from "./held-incomplete";
import { KIND_CODES, isKindCode, type KindCode } from "./kinds";

export type ParsedMa = {
  kind: KindCode;
  n: number;
};

const MA_RE = new RegExp(`^([${KIND_CODES.join("")}])(\\d{2,})$`, "i");

export function parseHubMa(raw: string): ParsedMa | null {
  const match = raw.trim().toUpperCase().match(MA_RE);
  if (!match) return null;
  const kind = match[1].toUpperCase();
  if (!isKindCode(kind)) return null;
  const n = Number(match[2]);
  if (!Number.isInteger(n) || n < 1 || n > 999) return null;
  return { kind, n };
}

export function formatMa(kind: KindCode, n: number): string {
  const digits = n < 100 ? String(n).padStart(2, "0") : String(n);
  return `${kind}${digits}`;
}

export function normalizeMa(raw: string): string {
  const parsed = parseHubMa(raw);
  return parsed ? formatMa(parsed.kind, parsed.n) : raw.trim().toUpperCase();
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
  return formatMa(kind, n);
}

function numbersForKind(kind: KindCode, mas: readonly string[]): Set<number> {
  const numbers = new Set<number>();
  for (const ma of mas) {
    const parsed = parseHubMa(ma);
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
