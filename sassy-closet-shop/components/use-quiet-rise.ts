"use client";

import { useEffect, useRef, type RefObject } from "react";
import { usePrefersReducedMotion } from "@/components/use-prefers-reduced-motion";

/**
 * Translate a block in when it enters. Opacity stays 1.
 * Blocks already on screen are left alone so covers never start hidden.
 */
export function useQuietRise<T extends HTMLElement>(): RefObject<T | null> {
  const ref = useRef<T>(null);
  const reduced = usePrefersReducedMotion();

  useEffect(() => {
    const el = ref.current;
    if (!el || reduced) {
      if (el) {
        delete el.dataset.rise;
      }
      return;
    }
    const rect = el.getBoundingClientRect();
    const alreadyVisible = rect.top < window.innerHeight * 0.92 && rect.bottom > 0;
    if (alreadyVisible) {
      return;
    }
    el.dataset.rise = "pending";
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          el.dataset.rise = "shown";
          observer.disconnect();
        }
      },
      { rootMargin: "0px 0px -6% 0px", threshold: 0.16 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [reduced]);

  return ref;
}
