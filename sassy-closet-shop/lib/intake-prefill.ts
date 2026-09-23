import type { IntakePrefill } from "@/lib/intake-import";

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
    if (typeof parsed.intakeMa !== "string" || !parsed.intakeMa.trim()) {
      return null;
    }
    return parsed as IntakePrefill;
  } catch {
    return null;
  }
}
