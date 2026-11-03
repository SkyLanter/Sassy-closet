"use client";

import { createContext, useCallback, useContext, useMemo, useState, type MouseEvent, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { SHOP_SEARCH_STORAGE_KEYS, type LookSearchItem } from "@/lib/look-search";

type ShopSearchContextValue = {
  looks: LookSearchItem[];
  draft: string | null;
  setDraft: (value: string | null) => void;
  clearSearch: () => void;
};

const ShopSearchContext = createContext<ShopSearchContextValue | null>(null);

function clearStoredShopSearch(): void {
  for (const key of SHOP_SEARCH_STORAGE_KEYS) {
    window.localStorage.removeItem(key);
    window.sessionStorage.removeItem(key);
  }
}

export function ShopSearchProvider({
  looks,
  initialQuery = "",
  children,
}: {
  looks: LookSearchItem[];
  initialQuery?: string;
  children: ReactNode;
}) {
  const router = useRouter();
  const trimmed = initialQuery.trim();
  const [draft, setDraft] = useState<string | null>(trimmed ? trimmed : null);
  const clearSearch = useCallback(() => {
    setDraft("");
    if (typeof window === "undefined") {
      return;
    }
    clearStoredShopSearch();
    const params = new URLSearchParams(window.location.search);
    const q = (params.get("q") ?? "").trim();
    const dirty = window.location.pathname !== "/" || q.length > 0;
    if (dirty) {
      router.push("/");
    }
  }, [router]);
  const value = useMemo(
    () => ({ looks, draft, setDraft, clearSearch }),
    [clearSearch, draft, looks],
  );

  return <ShopSearchContext.Provider value={value}>{children}</ShopSearchContext.Provider>;
}

/** Plain click on the wordmark goes to an unfiltered home. Modified clicks keep the browser default. */
export function onShopHomeClick(event: MouseEvent<HTMLAnchorElement>, clearSearch: () => void): void {
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) {
    return;
  }
  event.preventDefault();
  clearSearch();
}

export function useShopSearch(): ShopSearchContextValue {
  const context = useContext(ShopSearchContext);
  if (!context) {
    throw new Error("useShopSearch must be used within ShopSearchProvider");
  }
  return context;
}
