import type { ReactNode } from "react";

export function AdminFrame({ children }: { children: ReactNode }) {
  return (
    <div
      data-save-contract="blob+revalidate"
      data-next-ma-trap="off"
      data-allowlist-tiles="hub-ten"
      className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-12"
    >
      {children}
    </div>
  );
}
