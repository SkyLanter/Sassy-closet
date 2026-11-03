"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import type { MaLetter } from "@/lib/ma";

export type CategorySpyId = "all" | MaLetter;

type CategorySpyValue = {
  active: CategorySpyId | null;
  setActive: (next: CategorySpyId | null) => void;
};

const CategorySpyContext = createContext<CategorySpyValue | null>(null);

export function CategorySpyProvider({ children }: { children: ReactNode }) {
  const [active, setActive] = useState<CategorySpyId | null>(null);
  const value = useMemo(() => ({ active, setActive }), [active]);
  return <CategorySpyContext.Provider value={value}>{children}</CategorySpyContext.Provider>;
}

export function useCategorySpy(): CategorySpyValue {
  return (
    useContext(CategorySpyContext) ?? {
      active: null,
      setActive: () => {},
    }
  );
}
