"use client";

import { useEffect } from "react";
import { isOpaqueRscError } from "@/lib/opaque-rsc-error";

export default function AdminError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  const opaque = isOpaqueRscError(error);

  return (
    <div className="px-6 py-16">
      <p className="text-[11px] uppercase tracking-[0.18em] text-muted">Sell ops</p>
      <h1 className="mt-2 font-display text-4xl text-ink">Could not refresh this page</h1>
      <p className="mt-3 max-w-xl text-sm text-gold-deep">
        {opaque
          ? "The catalog may already be saved. Open Catalog and look for the new mã — do not Save again until you check."
          : error.message}
      </p>
      <div className="mt-6 flex flex-wrap gap-3">
        <a href="/admin" className="rounded-full bg-ink px-4 py-2 text-sm text-paper">
          Open catalog
        </a>
        <button
          type="button"
          onClick={reset}
          className="rounded-full border border-line px-4 py-2 text-sm text-ink"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
