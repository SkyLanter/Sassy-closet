import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

/** Customer shop has no admin desk. Catalog edits live on the intake app. */
export default function AdminLayout({ children }: { children: ReactNode }) {
  void children;
  notFound();
}
