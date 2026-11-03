"use client";

import { usePathname } from "next/navigation";
import { SKIP_TO_LOOKS } from "@/lib/pdp-copy";

export function SkipToLooks() {
  const pathname = usePathname();
  const href = pathname === "/" ? "#looks-heading" : "#main";

  return (
    <a
      href={href}
      data-testid="skip-to-looks"
      className="sr-only focus:not-sr-only focus:absolute focus:z-[80] focus:inline-flex focus:min-h-11 focus:items-center focus:border focus:border-gold/45 focus:liquid-glass-chip focus:px-3 focus:py-2 focus:text-sm focus:text-ink touch-manipulation select-none whitespace-nowrap"
      translate="no"
      style={{
        top: "max(0.75rem, env(safe-area-inset-top, 0px))",
        left: "max(1rem, env(safe-area-inset-left, 0px))",
      }}
    >
      {SKIP_TO_LOOKS}
    </a>
  );
}
