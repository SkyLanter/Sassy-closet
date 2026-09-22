"use client";

import { useEffect, useId, useRef, useState } from "react";
import {
  formatCm,
  hasAnyFitCm,
  hidesEmptyAsiaLetterRow,
  inboxForFitLine,
} from "@/lib/asia-size";
import type { Product } from "@/lib/types";

export function AsiaFit({ product }: { product: Product }) {
  const letters = product.sizes;
  const hideLetters = letters.length === 0 && hidesEmptyAsiaLetterRow(product.type);
  const showCm = hasAnyFitCm(product.fitCm);
  if (hideLetters && !showCm) {
    return null;
  }

  return (
    <div className="mt-6 space-y-3" data-testid="asia-fit">
      {hideLetters ? null : (
        <div>
          <p className="mb-2 text-[10px] uppercase tracking-[0.16em] text-muted">Asia size</p>
          {letters.length === 0 ? (
            <p className="text-sm text-muted" data-testid="asia-fit-empty">
              {inboxForFitLine(product.ma)}
            </p>
          ) : (
            <div className="flex flex-wrap gap-1.5" role="list" aria-label="Asia size">
              {letters.map((letter) => (
                <span
                  key={letter}
                  role="listitem"
                  data-testid="shop-size-pill"
                  className="rounded-full border border-ink bg-ink px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.12em] text-paper"
                >
                  {letter}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
      {showCm ? <FitCmSheet fit={product.fitCm} /> : null}
    </div>
  );
}

function FitCmSheet({
  fit,
}: {
  fit: Product["fitCm"];
}) {
  const [open, setOpen] = useState(false);
  const closeRef = useRef<HTMLButtonElement>(null);
  const titleId = useId();

  useEffect(() => {
    if (!open) {
      return;
    }
    closeRef.current?.focus();
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        setOpen(false);
      }
    }
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = overflow;
    };
  }, [open]);

  const rows: Array<{ label: string; value: number | null }> = [
    { label: "Bust / chest", value: fit.bustChestCm },
    { label: "Waist", value: fit.waistCm },
    { label: "Length", value: fit.lengthCm },
  ];

  return (
    <div>
      <button
        type="button"
        data-testid="fit-cm-open"
        onClick={() => setOpen(true)}
        className="rounded-full border border-line px-3 py-1.5 text-[10px] uppercase tracking-[0.14em] text-ink hover:border-gold"
      >
        Fit (cm)
      </button>
      {open ? (
        <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center">
          <button
            type="button"
            aria-label="Close fit"
            className="absolute inset-0 bg-ink/40"
            onClick={() => setOpen(false)}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            className="relative z-[1] w-full max-w-md rounded-t-2xl border border-line bg-paper p-6 shadow-[0_18px_40px_-24px_rgba(17,17,17,0.45)] sm:rounded-2xl"
          >
            <div className="flex items-start justify-between gap-3">
              <h2 id={titleId} className="font-display text-2xl text-ink">
                Fit · cm
              </h2>
              <button
                ref={closeRef}
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-full border border-line px-3 py-1 text-[10px] uppercase tracking-[0.14em] text-muted hover:border-gold hover:text-ink"
              >
                Close
              </button>
            </div>
            <dl className="mt-4 space-y-2 text-sm">
              {rows.map((row) =>
                row.value === null ? null : (
                  <div key={row.label} className="flex justify-between gap-4 border-b border-line py-2">
                    <dt className="text-muted">{row.label}</dt>
                    <dd className="tabular-nums text-ink">{formatCm(row.value)}</dd>
                  </div>
                ),
              )}
            </dl>
            <p className="mt-4 text-[11px] text-muted">Stored measurements only. Nothing is guessed from a letter.</p>
          </div>
        </div>
      ) : null}
    </div>
  );
}
