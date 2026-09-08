import { isKindCode, type KindCode } from "./kinds";

export type ParsedMa = {
  kind: KindCode;
  n: number;
};

const MA_RE = /^([AQVKGBPHJSO])(\d{2,})$/i;

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

export function nextMa(kind: KindCode, existing: string[]): string {
  let max = 0;
  for (const ma of existing) {
    const parsed = parseHubMa(ma);
    if (parsed && parsed.kind === kind) {
      max = Math.max(max, parsed.n);
    }
  }
  return formatMa(kind, max + 1);
}

export function maExists(existing: string[], ma: string, except?: string): boolean {
  const target = normalizeMa(ma);
  const skip = except ? normalizeMa(except) : "";
  return existing.some((item) => {
    const value = normalizeMa(item);
    return value === target && value !== skip;
  });
}
