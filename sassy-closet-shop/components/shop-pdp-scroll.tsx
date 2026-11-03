"use client";

import { useLayoutEffect } from "react";
import { usePathname } from "next/navigation";

/** Shared shop layout keeps window scroll; mã PDPs must open at the title, not under chrome. */
export function ShopPdpScroll() {
  const pathname = usePathname();

  useLayoutEffect(() => {
    if (!pathname.startsWith("/m/")) {
      return;
    }
    const html = document.documentElement;
    const previous = html.style.scrollBehavior;
    html.style.scrollBehavior = "auto";
    window.scrollTo(0, 0);
    html.style.scrollBehavior = previous;
  }, [pathname]);

  return null;
}
