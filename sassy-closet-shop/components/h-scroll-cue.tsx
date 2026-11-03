"use client";

import { useEffect, useRef, type ReactNode } from "react";

function horizontalScrollers(root: HTMLElement): HTMLElement[] {
  const nodes = [root, ...root.querySelectorAll<HTMLElement>("*")];
  return nodes.filter((node) => {
    const overflow = getComputedStyle(node).overflowX;
    return overflow === "auto" || overflow === "scroll";
  });
}

function syncFades(root: HTMLElement) {
  const scrollers = horizontalScrollers(root);
  let fadeLeft = false;
  let fadeRight = false;
  for (const scroller of scrollers) {
    const max = scroller.scrollWidth - scroller.clientWidth;
    if (max <= 2) {
      continue;
    }
    if (scroller.scrollLeft > 2) {
      fadeLeft = true;
    }
    if (scroller.scrollLeft < max - 2) {
      fadeRight = true;
    }
  }
  root.dataset.fadeLeft = fadeLeft ? "true" : "false";
  root.dataset.fadeRight = fadeRight ? "true" : "false";
}

export function HScrollCue({
  className,
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = ref.current;
    if (!root) {
      return;
    }
    const update = () => syncFades(root);
    update();
    root.addEventListener("scroll", update, { passive: true, capture: true });
    const observer = new ResizeObserver(update);
    observer.observe(root);
    for (const scroller of horizontalScrollers(root)) {
      observer.observe(scroller);
    }
    return () => {
      root.removeEventListener("scroll", update, { capture: true });
      observer.disconnect();
    };
  }, []);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
