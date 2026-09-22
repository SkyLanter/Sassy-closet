"use client";

import { useEffect, useState } from "react";
import { ANNOUNCEMENT_LINES, isLegacyAnnouncement } from "@/lib/trust-copy";

export function AnnouncementBar({ lines }: { lines: string[] }) {
  const safe =
    lines.length > 0 && !isLegacyAnnouncement(lines) ? lines : [...ANNOUNCEMENT_LINES];
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    function start() {
      if (media.matches || safe.length < 2 || document.hidden || paused) {
        return undefined;
      }
      return window.setInterval(() => {
        setIndex((current) => (current + 1) % safe.length);
      }, 4200);
    }
    let id = start();
    function restart() {
      if (id !== undefined) {
        window.clearInterval(id);
      }
      id = start();
    }
    media.addEventListener("change", restart);
    document.addEventListener("visibilitychange", restart);
    return () => {
      if (id !== undefined) {
        window.clearInterval(id);
      }
      media.removeEventListener("change", restart);
      document.removeEventListener("visibilitychange", restart);
    };
  }, [paused, safe.length]);

  return (
    <div
      className="relative z-[60] flex min-h-8 items-center justify-center overflow-hidden bg-ink text-paper"
      onPointerEnter={() => {
        if (window.matchMedia("(hover: hover)").matches) {
          setPaused(true);
        }
      }}
      onPointerLeave={() => setPaused(false)}
      style={{
        paddingTop: "env(safe-area-inset-top, 0px)",
        paddingLeft: "max(1rem, env(safe-area-inset-left, 0px))",
        paddingRight: "max(1rem, env(safe-area-inset-right, 0px))",
      }}
    >
      <p
        key={index}
        aria-live="polite"
        aria-atomic="true"
        className="announce-fade select-none whitespace-nowrap text-center text-[11px] font-medium uppercase tracking-[0.18em]"
        translate="no"
      >
        {safe[index]}
      </p>
    </div>
  );
}
