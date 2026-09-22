"use client";

import { useState } from "react";
import { copyMaDone, copyMaDoneAria, copyMaLabel } from "@/lib/pdp-copy";

export function CopyMa({ ma }: { ma: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(ma);
    } catch {
      const field = document.createElement("textarea");
      field.value = ma;
      field.setAttribute("readonly", "");
      field.style.position = "fixed";
      field.style.left = "-9999px";
      document.body.appendChild(field);
      field.select();
      document.execCommand("copy");
      document.body.removeChild(field);
    }
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
      className={`inline-flex min-h-11 touch-manipulation select-none items-center rounded-full border px-2.5 text-[10px] uppercase tracking-[0.16em] ${
        copied
          ? "border-gold text-ink"
          : "border-line text-muted hover-hover:hover:border-gold hover-hover:hover:text-ink"
      }`}
    >
      {copied ? copyMaDone(ma) : `Copy ${ma}`}
    </button>
  );
}
