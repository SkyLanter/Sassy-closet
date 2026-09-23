import type { Metadata } from "next";
import type { ReactNode } from "react";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

export default function AdminLayout({ children }: { children: ReactNode }) {
  return <div className="flex min-h-full flex-1 flex-col bg-paper">{children}</div>;
}
