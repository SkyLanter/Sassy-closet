"use client";

import { createContext, useContext, useSyncExternalStore, type ReactNode } from "react";
import { isMessengerAppDevice } from "@/lib/messenger";

const MessengerDeviceContext = createContext(false);

export function MessengerDeviceProvider({
  isAppDevice,
  children,
}: {
  isAppDevice: boolean;
  children: ReactNode;
}) {
  return (
    <MessengerDeviceContext.Provider value={isAppDevice}>{children}</MessengerDeviceContext.Provider>
  );
}

function clientChMobile(): string {
  const data = (navigator as Navigator & { userAgentData?: { mobile?: boolean } }).userAgentData;
  return data?.mobile === true ? "?1" : "";
}

function subscribe(): () => void {
  // The UA never changes for the life of the page; nothing to resubscribe.
  return () => {};
}

function getClientSnapshot(): boolean {
  return isMessengerAppDevice(
    navigator.userAgent,
    navigator.maxTouchPoints || 0,
    clientChMobile(),
  );
}

export function useMessengerAppDevice(): boolean {
  const serverIsApp = useContext(MessengerDeviceContext);
  // Server + hydration render from the UA-flagged context value so markup
  // matches; the client snapshot takes over after hydration.
  return useSyncExternalStore(subscribe, getClientSnapshot, () => serverIsApp);
}
