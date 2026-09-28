import type { Metadata } from "next";
import type { ReactNode } from "react";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Shop tools",
  robots: { index: false, follow: false },
};

export default function ShopToolsLayout({ children }: { children: ReactNode }) {
  return children;
}
