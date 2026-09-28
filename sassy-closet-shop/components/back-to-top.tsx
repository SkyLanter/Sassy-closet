"use client";

import { useEffect, useState } from "react";

const SHOW_AFTER = 720;

export function BackToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setVisible(window.scrollY > SHOW_AFTER);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (!visible) {
    return null;
  }

  return (
    <button
      type="button"
      className="sc-to-top liquid-glass-chip inline-flex h-11 w-11 touch-manipulation items-center justify-center rounded-full text-ink"
      aria-label="Lên đầu trang · Back to top"
      data-testid="back-to-top"
      onClick={() => {
        const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
      }}
    >
      <span aria-hidden className="font-display text-[1.35rem] leading-none">
        ↑
      </span>
    </button>
  );
}
