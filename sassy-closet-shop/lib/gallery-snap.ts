export type GalleryPeekEdge = "start" | "end" | "both" | "none";
export type GalleryRailAlign = "center" | "start";

/** Paper-edge mask only when a real neighbor exists. n=1 → none (no fake clone). */
export function galleryPeekEdge(index: number, count: number): GalleryPeekEdge {
  if (count <= 1) {
    return peekEdge("none");
  }
  if (index <= 0) {
    return peekEdge("start");
  }
  if (index >= count - 1) {
    return peekEdge("end");
  }
  return peekEdge("both");
}

function peekEdge(edge: GalleryPeekEdge): GalleryPeekEdge {
  switch (edge) {
    case "start":
    case "end":
    case "both":
    case "none":
      return edge;
    default: {
      const _exhaustive: never = edge;
      return _exhaustive;
    }
  }
}

export function clampGalleryIndex(next: number, count: number): number {
  if (count <= 0) {
    return 0;
  }
  return Math.min(count - 1, Math.max(0, next));
}

/** Color / peek roll. Fast OFF: viscous one-shot, not a 150ms jump and not a 700ms luxury wipe. */
export const GALLERY_ROLL_MS = 440;

export function galleryScrollBehavior(reduced: boolean): ScrollBehavior {
  return reduced ? "instant" : "smooth";
}

/** Stronger end-snap than cubic — the photo settles, it does not drift. */
function easeOutQuint(t: number): number {
  return 1 - (1 - t) ** 5;
}

function railAlignDelta(railBox: DOMRect, itemBox: DOMRect, align: GalleryRailAlign): number {
  switch (align) {
    case "start":
      return itemBox.left - railBox.left;
    case "center":
      return itemBox.left + itemBox.width / 2 - (railBox.left + railBox.width / 2);
    default: {
      const _exhaustive: never = align;
      return _exhaustive;
    }
  }
}

/** Horizontal snap. Rail `scrollLeft` only — never page `scrollIntoView`. */
export function scrollRailToChild(
  rail: HTMLElement | null,
  current: HTMLElement | null,
  align: GalleryRailAlign = "center",
): void {
  if (!rail || !current) {
    return;
  }
  const delta = railAlignDelta(rail.getBoundingClientRect(), current.getBoundingClientRect(), align);
  if (Math.abs(delta) < 0.5) {
    return;
  }
  rail.scrollLeft += delta;
}

/** Programmatic gallery roll. Never Motion-drag the snap port. Reduce = instant. */
export function animateGalleryScrollTo(
  port: HTMLElement,
  slide: HTMLElement,
  reduced: boolean,
  onDone?: () => void,
): () => void {
  if (reduced) {
    scrollRailToChild(port, slide, "center");
    onDone?.();
    return () => {};
  }
  const delta = railAlignDelta(port.getBoundingClientRect(), slide.getBoundingClientRect(), "center");
  const start = port.scrollLeft;
  const end = start + delta;
  if (Math.abs(delta) < 0.5) {
    onDone?.();
    return () => {};
  }
  const previousSnap = port.style.scrollSnapType;
  const previousBehavior = port.style.scrollBehavior;
  port.style.scrollSnapType = "none";
  port.style.scrollBehavior = "auto";
  let raf = 0;
  let cancelled = false;
  const started = performance.now();
  const finish = () => {
    port.style.scrollSnapType = previousSnap;
    port.style.scrollBehavior = previousBehavior;
    if (!cancelled) {
      scrollRailToChild(port, slide, "center");
      onDone?.();
    }
  };
  const tick = (now: number) => {
    if (cancelled) {
      return;
    }
    const t = Math.min(1, (now - started) / GALLERY_ROLL_MS);
    port.scrollLeft = start + (end - start) * easeOutQuint(t);
    if (t < 1) {
      raf = requestAnimationFrame(tick);
      return;
    }
    finish();
  };
  raf = requestAnimationFrame(tick);
  return () => {
    cancelled = true;
    cancelAnimationFrame(raf);
    port.style.scrollSnapType = previousSnap;
    port.style.scrollBehavior = previousBehavior;
  };
}

export function nearestCenteredIndex(
  port: HTMLElement,
  nodes: Array<HTMLElement | null>,
): number {
  const portBox = port.getBoundingClientRect();
  const center = portBox.left + portBox.width / 2;
  let best = 0;
  let bestDist = Number.POSITIVE_INFINITY;
  nodes.forEach((node, i) => {
    if (!node) {
      return;
    }
    const box = node.getBoundingClientRect();
    const dist = Math.abs(box.left + box.width / 2 - center);
    if (dist < bestDist) {
      best = i;
      bestDist = dist;
    }
  });
  return best;
}

export function nearestStartIndex(
  port: HTMLElement,
  nodes: Array<HTMLElement | null>,
): number {
  const left = port.getBoundingClientRect().left;
  let best = 0;
  let bestDist = Number.POSITIVE_INFINITY;
  nodes.forEach((node, i) => {
    if (!node) {
      return;
    }
    const box = node.getBoundingClientRect();
    const dist = Math.abs(box.left - left);
    if (dist < bestDist) {
      best = i;
      bestDist = dist;
    }
  });
  return best;
}

/**
 * Horizontal chrome (thumbs / dots / featured tabs).
 * Rail `scrollLeft` only — never page `scrollIntoView` (that yanks the look).
 */
export function scrollChromeChildIntoView(
  rail: HTMLElement | null,
  current: HTMLElement | null,
): void {
  if (!rail || !current) {
    return;
  }
  const railBox = rail.getBoundingClientRect();
  const itemBox = current.getBoundingClientRect();
  if (itemBox.left >= railBox.left && itemBox.right <= railBox.right) {
    return;
  }
  scrollRailToChild(rail, current, "center");
}

export function scrollCurrentChromeIntoView(rail: HTMLElement | null): void {
  if (!rail) {
    return;
  }
  scrollChromeChildIntoView(rail, rail.querySelector<HTMLElement>('[aria-current="true"]'));
}
