import { nextMa, parseHubMa } from "./mint";
import type { KindCode } from "./kinds";

export function canSaveEdit(loadedMa: string | null): boolean {
  return Boolean(loadedMa);
}

export function renameAfterKindChange(
  loadedMa: string | null,
  nextKind: KindCode,
  knownMas: string[],
): string {
  if (!loadedMa) return "";
  const current = parseHubMa(loadedMa)?.kind;
  if (current && current !== nextKind) return nextMa(nextKind, knownMas);
  return "";
}

export function editSaveIntent(
  loadedMa: string | null,
  renameTo: string,
): { ma: string; renameTo: string | null } | null {
  if (!loadedMa) return null;
  const rename = renameTo.trim();
  return { ma: loadedMa, renameTo: rename || null };
}
