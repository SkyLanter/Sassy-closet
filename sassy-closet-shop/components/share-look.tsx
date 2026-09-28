"use client";

import { useState } from "react";
import { copyText } from "@/lib/copy-text";
import {
  SHARE_LOOK_DONE,
  SHARE_LOOK_LABEL,
  shareLookAria,
  shareLookDoneAria,
} from "@/lib/pdp-copy";

export function ShareLook({ ma, title }: { ma: string; title: string }) {
  const [copied, setCopied] = useState(false);

  async function share() {
    const url = new URL(`/m/${ma}`, window.location.origin).toString();
    if (typeof navigator.share === "function") {
      try {
        await navigator.share({ title, url });
        return;
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
      }
    }
    await copyText(url);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <button
      type="button"
      data-testid="share-look"
      aria-live="polite"
      aria-atomic="true"
      aria-label={copied ? shareLookDoneAria(ma) : shareLookAria(ma)}
      onClick={() => {
        void share();
      }}
      translate="no"
      className={`inline-flex min-h-11 min-w-11 touch-manipulation select-none items-center rounded-full border px-2.5 text-[10px] uppercase tracking-[0.16em] ${
        copied
          ? "border-gold text-ink"
          : "border-line text-muted hover-hover:hover:border-gold hover-hover:hover:text-ink"
      }`}
    >
      {copied ? SHARE_LOOK_DONE : SHARE_LOOK_LABEL}
    </button>
  );
}
