"use client";

import { createContext, useContext, type ReactNode } from "react";
import { defaultSiteSettings } from "@/lib/site-settings";
import type { SiteSettings } from "@/lib/types";

const SiteSettingsContext = createContext<SiteSettings>(defaultSiteSettings());

export function SiteSettingsProvider({
  settings,
  children,
}: {
  settings: SiteSettings;
  children: ReactNode;
}) {
  return <SiteSettingsContext.Provider value={settings}>{children}</SiteSettingsContext.Provider>;
}

export function useSiteSettings(): SiteSettings {
  return useContext(SiteSettingsContext);
}
