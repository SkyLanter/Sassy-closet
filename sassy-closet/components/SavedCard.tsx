"use client";

import { useEffect, useState } from "react";
import { captionStarter, editDeepLink, kindColorsLine } from "@/lib/captions";
import type { Submission } from "@/lib/types";

type CopyKind = "ma" | "link" | "caption" | null;

export function SavedCard({
  result,
  onClose,
}: {
  result: Submission | null;
  onClose: () => void;
}) {
  const [copied, setCopied] = useState<CopyKind>(null);

  useEffect(() => {
    setCopied(null);
  }, [result]);

  if (!result) return null;

  const line = kindColorsLine(result);
  const link = editDeepLink(window.location.origin, result.ma);
  const starter = captionStarter(result.ma);

  async function copy(kind: Exclude<CopyKind, null>, text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(kind);
    } catch {
      setCopied(null);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-rose-950/30 p-0 sm:items-center sm:p-6"
      role="presentation"
      onClick={onClose}
    >
      <section
        data-testid="saved-card"
        role="dialog"
        aria-labelledby="saved-card-title"
        className="w-full max-w-md rounded-t-3xl bg-[oklch(0.995_0.01_50)] p-5 shadow-xl sm:rounded-3xl lg:p-8"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="text-center">
          <h2
            id="saved-card-title"
            data-testid="saved-card-title"
            className="text-base font-bold text-rose-700 lg:text-xl"
          >
            Saved · Đã lưu
          </h2>
        </div>
        <p
          data-testid="saved-card-ma"
          className="mt-4 text-center text-5xl font-extrabold tracking-wide text-rose-700 lg:text-6xl"
        >
          {result.ma}
        </p>
        <p
          data-testid="saved-card-line"
          className="mt-2 text-center text-sm font-semibold text-rose-800"
        >
          {line}
        </p>
        <div className="mt-5 grid gap-2">
          <button
            type="button"
            data-testid="copy-ma"
            className="h-12 rounded-full bg-primary text-base font-bold text-primary-foreground"
            onClick={() => void copy("ma", result.ma)}
          >
            Copy mã
          </button>
          <button
            type="button"
            data-testid="copy-link"
            className="h-12 rounded-full bg-white text-base font-bold text-rose-800 ring-1 ring-rose-100"
            onClick={() => void copy("link", link)}
          >
            Copy link
          </button>
          <button
            type="button"
            data-testid="copy-caption"
            className="h-12 rounded-full bg-white text-base font-bold text-rose-800 ring-1 ring-rose-100"
            onClick={() => void copy("caption", starter)}
          >
            Copy caption starter
          </button>
        </div>
        {copied ? (
          <p
            data-testid="toast-copied"
            className="mt-3 rounded-full bg-rose-100 py-2 text-center text-sm font-semibold text-rose-800"
          >
            Đã copy
          </p>
        ) : null}
        <button
          type="button"
          data-testid="saved-card-done"
          className="mt-4 h-11 w-full rounded-full text-sm font-semibold text-rose-700"
          onClick={onClose}
        >
          Done
        </button>
      </section>
    </div>
  );
}
