"use client";

import { useEffect } from "react";
import { track } from "@vercel/analytics";

/** Records a product page open. Renders nothing. */
export function ProductViewEvent({ ma }: { ma: string }) {
  useEffect(() => {
    if (!ma) {
      return;
    }
    track("product_view", { ma });
  }, [ma]);

  return null;
}
