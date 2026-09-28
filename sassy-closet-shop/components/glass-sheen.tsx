"use client";

import { useEffect } from "react";

/** Moves the glass highlight a few percent. One rAF, no markup change. */
export function GlassSheen() {
  useEffect(() => {
    const root = document.documentElement;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
    const fine = window.matchMedia("(hover: hover) and (pointer: fine)");
    if (reduce.matches) {
      return;
    }

    let frame = 0;
    let pointerX = window.innerWidth * 0.28;
    let pointerY = window.innerHeight * 0.2;
    let scrollY = window.scrollY;

    const paint = () => {
      frame = 0;
      const width = Math.max(window.innerWidth, 1);
      const height = Math.max(window.innerHeight, 1);
      const x = 8 + (pointerX / width) * 22 + ((scrollY % 280) / 280) * 12;
      const y = 4 + (pointerY / height) * 16;
      root.style.setProperty("--glass-sheen-x", `${x.toFixed(1)}%`);
      root.style.setProperty("--glass-sheen-y", `${y.toFixed(1)}%`);
    };

    const schedule = () => {
      if (frame !== 0) {
        return;
      }
      frame = window.requestAnimationFrame(paint);
    };

    const onPointer = (event: PointerEvent) => {
      pointerX = event.clientX;
      pointerY = event.clientY;
      schedule();
    };

    const onScroll = () => {
      scrollY = window.scrollY;
      schedule();
    };

    const stop = () => {
      if (frame !== 0) {
        window.cancelAnimationFrame(frame);
        frame = 0;
      }
      window.removeEventListener("pointermove", onPointer);
      window.removeEventListener("scroll", onScroll);
      root.style.removeProperty("--glass-sheen-x");
      root.style.removeProperty("--glass-sheen-y");
    };

    const onReduce = () => {
      if (reduce.matches) {
        stop();
      }
    };

    if (fine.matches) {
      window.addEventListener("pointermove", onPointer, { passive: true });
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    reduce.addEventListener("change", onReduce);
    schedule();

    return () => {
      reduce.removeEventListener("change", onReduce);
      stop();
    };
  }, []);

  return null;
}
