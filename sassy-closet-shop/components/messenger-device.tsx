"use client";

import { createContext, useContext, useLayoutEffect, useState, type ReactNode } from "react";
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

export function useMessengerAppDevice(): boolean {
  const serverIsApp = useContext(MessengerDeviceContext);
  const [isAppDevice, setIsAppDevice] = useState(serverIsApp);

  useLayoutEffect(() => {
    setIsAppDevice(
      isMessengerAppDevice(
        navigator.userAgent,
        navigator.maxTouchPoints || 0,
        clientChMobile(),
      ),
    );
  }, []);

  return isAppDevice;
}
