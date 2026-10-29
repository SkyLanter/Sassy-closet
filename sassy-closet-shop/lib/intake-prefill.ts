import { isShopSize } from "@/lib/asia-size";
import type { IntakePrefill, PrefillColor } from "@/lib/intake-import";

const str = (value: unknown): string => (typeof value === "string" ? value : "");
const strList = (value: unknown): string[] =>
  Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];

/** Stale or hand-edited storage must not crash prefillToDraft on /admin/new. */
function sanitizePrefill(parsed: Partial<IntakePrefill> & { intakeMa: string }): IntakePrefill {
  const colors: PrefillColor[] = Array.isArray(parsed.colors)
    ? parsed.colors
        .filter((c): c is PrefillColor => Boolean(c) && typeof c === "object" && typeof c.name === "string")
        .map((c) => ({
          ...c,
          note: str(c.note),
          truth: c.truth === "confirmed" ? "confirmed" : "unconfirmed",
          source: str(c.source),
        }))
    : [];
  return {
    ...parsed,
    letter: str(parsed.letter),
    colors,
    sizes: strList(parsed.sizes).filter(isShopSize),
    droppedSizes: strList(parsed.droppedSizes),
    sourceLink: str(parsed.sourceLink),
    blurb: str(parsed.blurb),
    captionVi: str(parsed.captionVi),
    colorNote: str(parsed.colorNote),
    photoPaths: strList(parsed.photoPaths),
    photoLink: str(parsed.photoLink),
    createdAt: str(parsed.createdAt),
    warnings: strList(parsed.warnings),
  } as IntakePrefill;
}

/**
 * Carries an intake prefill from the Intake import page to /admin/new.
 * sessionStorage only — never a URL (colors/notes can be long), never the
 * server. Consumed once: reading removes it so a refresh cannot resurrect a
 * stale draft.
 */

const PREFILL_KEY = "sassy:intake-prefill:v1";

export function writeIntakePrefill(prefill: IntakePrefill): void {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.sessionStorage.setItem(PREFILL_KEY, JSON.stringify(prefill));
  } catch {
    // Storage full or blocked — the Add page simply opens empty.
  }
}

export function consumeIntakePrefill(): IntakePrefill | null {
  if (typeof window === "undefined") {
    return null;
  }
  let raw: string | null = null;
  try {
    raw = window.sessionStorage.getItem(PREFILL_KEY);
    window.sessionStorage.removeItem(PREFILL_KEY);
  } catch {
    return null;
  }
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw) as Partial<IntakePrefill>;
    if (!parsed || typeof parsed !== "object" || typeof parsed.intakeMa !== "string" || !parsed.intakeMa.trim()) {
      return null;
    }
    return sanitizePrefill(parsed as Partial<IntakePrefill> & { intakeMa: string });
  } catch {
    return null;
  }
}
