/** Slow boutique reveal: left→right soft sheen, then unmount. */
export const CONTENT_WAVE_MS = 1200;
/** Extra settle after the sheen exits before unmount. */
export const CONTENT_WAVE_HOLD_MS = 80;
/** Intro waits until this much of the looks stage is on screen (not under the hero). */
export const CONTENT_WAVE_INTRO_RATIO = 0.12;

/** Full one-shot including settle, then still. */
export function contentWaveDurationMs(): number {
  return CONTENT_WAVE_MS + CONTENT_WAVE_HOLD_MS;
}
