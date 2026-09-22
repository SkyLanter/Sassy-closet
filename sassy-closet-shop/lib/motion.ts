export const springSoft = {
  type: "spring" as const,
  stiffness: 420,
  damping: 32,
  mass: 0.72,
};

/** Featured count-line fade. Official #31: ≤200ms. */
export const FILTER_FADE_SECONDS = 0.18;

/** Featured grid watery pour. Fast (180ms fade-only) is off. */
export const FILTER_POUR_SECONDS = 0.32;

/** Color → gallery SET fade on this mã only. Official #31 / #36: 150–250ms opacity. */
export const COLOR_FADE_SECONDS = 0.2;

/** PDP hero: full-bleed on the named 3/4 frame. 78% / 12px neighbor peeks ate the product on phone. */
export const GALLERY_SLIDE_RATIO = 1;
export const GALLERY_GAP_PX = 0;

export function staggerContainer(reduced: boolean) {
  return {
    hidden: {},
    show: {
      transition: reduced
        ? { duration: 0 }
        : { staggerChildren: 0.07, delayChildren: 0.04 },
    },
  };
}

export const filterEase = [0.22, 1, 0.36, 1] as const;

/** 1 = later in the list (slide from the right), -1 = earlier (from the left). */
export function slideDirection(fromIndex: number, toIndex: number): number {
  return toIndex >= fromIndex ? 1 : -1;
}

/** Opacity-only filter for Featured tabs. Never leave opacity-0 ghosts. */
export function filterOpacity(reduced: boolean) {
  if (reduced) {
    return {
      initial: { opacity: 1 },
      animate: { opacity: 1, transition: { duration: 0 } },
      exit: { opacity: 1, transition: { duration: 0 } },
    };
  }
  return {
    initial: { opacity: 0.45 },
    animate: {
      opacity: 1,
      transition: { duration: FILTER_FADE_SECONDS, ease: filterEase },
    },
    exit: { opacity: 1, transition: { duration: 0 } },
  };
}

export function filterSlide(reduced: boolean, direction: number) {
  if (reduced) {
    return {
      initial: { opacity: 1, x: 0, clipPath: "inset(0)" },
      animate: { opacity: 1, x: 0, clipPath: "inset(0)", transition: { duration: 0 } },
      exit: { opacity: 1, x: 0, clipPath: "inset(0)", transition: { duration: 0 } },
    };
  }
  const pour = { duration: FILTER_POUR_SECONDS, ease: filterEase };
  const from =
    direction > 0
      ? "inset(0 0 0 28% round 0 56% 58% 0)"
      : "inset(0 28% 0 0 round 56% 0 0 58%)";
  const exitTo =
    direction > 0
      ? "inset(0 22% 0 0 round 48% 0 0 52%)"
      : "inset(0 0 0 22% round 0 48% 52% 0)";
  return {
    initial: { opacity: 1, x: 8 * direction, clipPath: from },
    animate: {
      opacity: 1,
      x: 0,
      clipPath: "inset(0)",
      transition: pour,
    },
    exit: {
      opacity: 1,
      x: -6 * direction,
      clipPath: exitTo,
      transition: { duration: 0.18, ease: filterEase },
    },
  };
}

/** Short frosted glass film on this mã’s color swap — never opacity-0 the photo. */
export function colorCrossfade(reduced: boolean) {
  if (reduced) {
    return {
      initial: { opacity: 0 },
      animate: { opacity: 0, transition: { duration: 0 } },
      exit: { opacity: 0, transition: { duration: 0 } },
    };
  }
  return {
    initial: { opacity: 0.28 },
    animate: {
      opacity: 0,
      transition: { duration: COLOR_FADE_SECONDS, ease: filterEase },
    },
    exit: { opacity: 0.18, transition: { duration: 0.14 } },
  };
}

/** Cards paint at opacity 1 even before JS. Never hide covers in `hidden`. */
export function fadeUp(reduced: boolean) {
  return {
    hidden: { opacity: 1, y: 0 },
    show: {
      opacity: 1,
      y: 0,
      transition: reduced ? { duration: 0 } : springSoft,
    },
    exit: reduced
      ? { opacity: 1, transition: { duration: 0 } }
      : { opacity: 1, y: 0, transition: { duration: 0.15 } },
  };
}
