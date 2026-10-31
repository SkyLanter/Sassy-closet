import type { Metadata } from "next";
import type { ReactNode } from "react";
import { INTAKE_LISTING_ROBOTS } from "@/lib/intake-direct-link-headers";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Shop tools",
  robots: INTAKE_LISTING_ROBOTS,
};

export default function ShopToolsLayout({ children }: { children: ReactNode }) {
  return children;
}
