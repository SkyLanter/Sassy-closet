"use client";

import { useLayoutEffect } from "react";
import { usePathname } from "next/navigation";

/** After a real navigation, land on the hash target (or the category section) without a long glide. */
export function CategoryLandingScroll({ sectionId }: { sectionId: string }) {
  const pathname = usePathname();

  useLayoutEffect(() => {
    const scroll = () => {
      const hash = window.location.hash.replace("#", "");
      const id = hash || sectionId;
      const node = document.getElementById(id);
      if (!node) {
        return;
      }
      node.scrollIntoView({ block: "start", behavior: "auto" });
    };
    scroll();
    const frame = window.requestAnimationFrame(scroll);
    return () => window.cancelAnimationFrame(frame);
  }, [pathname, sectionId]);

  return null;
}
