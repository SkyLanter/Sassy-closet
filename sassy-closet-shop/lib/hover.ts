"use client";

import { useSyncExternalStore } from "react";

function subscribe(onStoreChange: () => void): () => void {
  const media = window.matchMedia("(hover: hover)");
  media.addEventListener("change", onStoreChange);
  return () => media.removeEventListener("change", onStoreChange);
}

function getSnapshot(): boolean {
  return window.matchMedia("(hover: hover)").matches;
}

function getServerSnapshot(): boolean {
  return false;
}

/** True only when the pointer can hover. Touch stays tap-only so lift/scale never steal the first click. */
export function useCanHover(): boolean {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
