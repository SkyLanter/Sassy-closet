"use client";

import { createContext, useContext, type ReactNode } from "react";

const CatalogMediaVersionContext = createContext("");

export function CatalogMediaVersionProvider({
  version,
  children,
}: {
  version: string;
  children: ReactNode;
}) {
  return (
    <CatalogMediaVersionContext.Provider value={version}>
      {children}
    </CatalogMediaVersionContext.Provider>
  );
}

export function useCatalogMediaVersion(): string {
  return useContext(CatalogMediaVersionContext);
}
