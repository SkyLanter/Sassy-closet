"use client";

import { useEffect, useRef } from "react";
import { useAdminEntry } from "@/components/admin-entry";

/** Logo long-press for a signed-in desk session. Not part of the public header bundle. */
export function LogoAdminHold() {
  const studio = useAdminEntry();
  const openStudio = studio?.openStudio;
  const holdTimer = useRef<number | null>(null);
  const gated = useRef(false);

  useEffect(() => {
    if (!openStudio) {
      return;
    }
    const logo = document.querySelector<HTMLElement>('[data-testid="shop-logo"]');
    if (!logo) {
      return;
    }

    function clearHold() {
      if (holdTimer.current !== null) {
        window.clearTimeout(holdTimer.current);
        holdTimer.current = null;
      }
    }

    function startHold() {
      clearHold();
      gated.current = false;
      holdTimer.current = window.setTimeout(() => {
        gated.current = true;
        openStudio?.();
      }, 700);
    }

    function onClick(event: Event) {
      if (!gated.current) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      gated.current = false;
    }

    logo.addEventListener("pointerdown", startHold);
    logo.addEventListener("pointerup", clearHold);
    logo.addEventListener("pointercancel", clearHold);
    logo.addEventListener("pointerleave", clearHold);
    logo.addEventListener("click", onClick, true);
    return () => {
      clearHold();
      logo.removeEventListener("pointerdown", startHold);
      logo.removeEventListener("pointerup", clearHold);
      logo.removeEventListener("pointercancel", clearHold);
      logo.removeEventListener("pointerleave", clearHold);
      logo.removeEventListener("click", onClick, true);
    };
  }, [openStudio]);

  return null;
}
