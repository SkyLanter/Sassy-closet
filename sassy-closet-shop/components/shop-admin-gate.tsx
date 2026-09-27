"use client";

import dynamic from "next/dynamic";
import type { ReactNode } from "react";

const ShopAdminChrome = dynamic(() =>
  import("@/components/shop-admin-chrome").then((mod) => mod.ShopAdminChrome),
);

export function ShopAdminGate({
  enabled,
  children,
}: {
  enabled: boolean;
  children: ReactNode;
}) {
  if (!enabled) {
    return children;
  }
  return <ShopAdminChrome>{children}</ShopAdminChrome>;
}
