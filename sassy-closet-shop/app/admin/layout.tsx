import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AdminSignOut } from "@/app/admin/sign-out";
import { hasAdminSession } from "@/lib/admin-session-request";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

export default async function AdminLayout({ children }: { children: ReactNode }) {
  const signedIn = await hasAdminSession();
  return (
    <div className="flex min-h-full flex-1 flex-col bg-paper">
      {signedIn ? <AdminSignOut /> : null}
      {children}
    </div>
  );
}
