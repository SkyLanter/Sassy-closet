"use client";

import { useState } from "react";
import { copyText } from "@/lib/copy-text";
import { copyMaDone, copyMaDoneAria, copyMaLabel } from "@/lib/pdp-copy";

export function CopyMa({ ma }: { ma: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await copyText(ma);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <button
      type="button"
      data-testid="copy-ma"
      aria-live="polite"
      aria-atomic="true"
      aria-label={copied ? copyMaDoneAria(ma) : copyMaLabel(ma)}
      onClick={() => {
        void copy();
      }}
      translate="no"
      className={`liquid-glass-chip inline-flex min-h-11 shrink-0 touch-manipulation select-none items-center whitespace-nowrap rounded-full border px-2.5 text-[11px] uppercase tracking-[0.16em] ${
        copied
          ? "border-gold text-ink"
          : "border-line text-muted hover-hover:hover:border-gold hover-hover:hover:text-ink"
      }`}
    >
      {copied ? copyMaDone(ma) : `Copy ${ma}`}
    </button>
  );
}
