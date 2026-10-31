import type { Metadata } from "next";
import type { ReactNode } from "react";
import { INTAKE_LISTING_ROBOTS } from "@/lib/intake-direct-link-headers";

export const dynamic = "force-dynamic";

/** CSV desk and shop tools stay noindex with the public form. */
export const metadata: Metadata = {
  robots: INTAKE_LISTING_ROBOTS,
};

export default function AdminLayout({ children }: { children: ReactNode }) {
  return children;
}
