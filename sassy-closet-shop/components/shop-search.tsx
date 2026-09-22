"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import type { LookSearchItem } from "@/lib/look-search";

type ShopSearchContextValue = {
  looks: LookSearchItem[];
  draft: string | null;
  setDraft: (value: string | null) => void;
};

const ShopSearchContext = createContext<ShopSearchContextValue | null>(null);

export function ShopSearchProvider({
  looks,
  initialQuery = "",
  children,
}: {
  looks: LookSearchItem[];
  initialQuery?: string;
  children: ReactNode;
}) {
  const trimmed = initialQuery.trim();
  const [draft, setDraft] = useState<string | null>(trimmed ? trimmed : null);
  const value = useMemo(
    () => ({ looks, draft, setDraft }),
    [draft, looks],
  );

  return <ShopSearchContext.Provider value={value}>{children}</ShopSearchContext.Provider>;
}

export function useShopSearch(): ShopSearchContextValue {
  const context = useContext(ShopSearchContext);
  if (!context) {
    throw new Error("useShopSearch must be used within ShopSearchProvider");
  }
  return context;
}
