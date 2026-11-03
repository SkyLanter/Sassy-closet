"use client";

import { useEffect } from "react";
import { track } from "@vercel/analytics";

/** Records a product page open. Renders nothing. */
export function ProductViewEvent({ ma }: { ma: string }) {
  useEffect(() => {
    if (!ma) {
      return;
    }
    // <Analytics /> installs window.va in a later effect. Track after that flush
    // so the first open is queued instead of dropped.
    let cancelled = false;
    queueMicrotask(() => {
      if (!cancelled) {
        track("product_view", { ma });
      }
    });
    return () => {
      cancelled = true;
    };
  }, [ma]);

  return null;
}
