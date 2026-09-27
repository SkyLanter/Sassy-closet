"use client";

import type { ReactNode } from "react";
import { AdminEntryProvider } from "@/components/admin-entry";
import { LogoAdminHold } from "@/components/logo-admin-hold";

/** Gold-dot shop tools. Rendered only when the admin session cookie is valid. */
export function ShopAdminChrome({ children }: { children: ReactNode }) {
  return (
    <AdminEntryProvider>
      <LogoAdminHold />
      {children}
    </AdminEntryProvider>
  );
}
