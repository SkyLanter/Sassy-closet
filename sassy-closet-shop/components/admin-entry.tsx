"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useId,
  useRef,
  useState,
  type ReactNode,
} from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

type AdminEntryContextValue = {
  openStudio: () => void;
};

const AdminEntryContext = createContext<AdminEntryContextValue | null>(null);

export function useAdminEntry(): AdminEntryContextValue | null {
  return useContext(AdminEntryContext);
}

export function AdminEntryProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const aboveShipBar = pathname.startsWith("/m/");
  const openStudio = useCallback(() => setOpen(true), []);
  const close = useCallback(() => setOpen(false), []);

  return (
    <AdminEntryContext.Provider value={{ openStudio }}>
      {children}
      <button
        type="button"
        onClick={openStudio}
        className={`fixed z-50 flex h-11 w-11 touch-manipulation items-center justify-center right-[max(0.75rem,env(safe-area-inset-right,0px))] ${
          aboveShipBar
            ? "bottom-[max(7rem,calc(5.5rem+env(safe-area-inset-bottom,0px)))] md:bottom-[max(0.75rem,env(safe-area-inset-bottom,0px))]"
            : "bottom-[max(0.75rem,env(safe-area-inset-bottom,0px))]"
        }`}
        aria-label="Công cụ shop · Shop tools"
        aria-haspopup="dialog"
        aria-expanded={open}
      >
        <span className="h-2.5 w-2.5 rounded-full bg-gold/70 hover-hover:hover:bg-gold" aria-hidden />
      </button>
      {open ? <AdminGateModal onClose={close} /> : null}
    </AdminEntryContext.Provider>
  );
}

function AdminGateModal({ onClose }: { onClose: () => void }) {
  const titleId = useId();
  const closeRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    previousFocus.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
    closeRef.current?.focus();
    const overflow = document.body.style.overflow;
    const htmlOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";
    const inerted = [
      document.getElementById("main"),
      document.querySelector('[data-testid="shop-chrome"]'),
      document.querySelector("footer"),
      document.querySelector('a[href="#main"]'),
      document.querySelector('[aria-label="Công cụ shop · Shop tools"]'),
    ].filter((node): node is HTMLElement => node instanceof HTMLElement);
    for (const node of inerted) {
      node.inert = true;
    }
    function onKey(event: KeyboardEvent) {
      switch (event.key) {
        case "Escape":
          event.preventDefault();
          onClose();
          return;
        case "Tab": {
          const root = dialogRef.current;
          if (!root) {
            return;
          }
          const focusable = [
            ...root.querySelectorAll<HTMLElement>("button, a[href]"),
          ].filter((node) => !node.hasAttribute("disabled") && node.tabIndex >= 0);
          if (focusable.length === 0) {
            return;
          }
          const first = focusable[0];
          const last = focusable[focusable.length - 1];
          const active = document.activeElement;
          if (event.shiftKey && active === first) {
            event.preventDefault();
            last?.focus();
          } else if (!event.shiftKey && active === last) {
            event.preventDefault();
            first?.focus();
          }
          return;
        }
        default:
          return;
      }
    }
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = overflow;
      document.documentElement.style.overflow = htmlOverflow;
      for (const node of inerted) {
        node.inert = false;
      }
      previousFocus.current?.focus();
    };
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-[80] flex items-end justify-center overscroll-contain bg-ink/35 sm:items-center"
      style={{
        paddingBottom: "max(1rem, env(safe-area-inset-bottom, 0px))",
        paddingTop: "max(1rem, env(safe-area-inset-top, 0px))",
        paddingLeft: "max(1rem, env(safe-area-inset-left, 0px))",
        paddingRight: "max(1rem, env(safe-area-inset-right, 0px))",
      }}
    >
      <button
        type="button"
        className="absolute inset-0 cursor-default"
        aria-label="Đóng"
        tabIndex={-1}
        onClick={onClose}
      />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="relative w-full max-w-sm rounded-2xl border border-gold/45 bg-paper px-6 py-7 shadow-xl"
      >
        <h2 id={titleId} className="font-display text-3xl leading-[1.08] text-ink" translate="no">
          Shop tools
        </h2>
        <p className="mt-2 text-pretty text-sm text-muted" translate="no">Test catalog editor. Not linked in the main nav.</p>
        <Link
          href="/admin"
          translate="no"
          className="mt-6 inline-flex min-h-11 touch-manipulation items-center rounded-full bg-ink px-5 py-2.5 text-sm text-paper hover-hover:hover:opacity-90"
        >
          Open admin
        </Link>
        <button
          ref={closeRef}
          type="button"
          onClick={onClose}
          translate="no"
          className="ml-3 inline-flex min-h-11 touch-manipulation items-center text-sm text-muted hover-hover:hover:text-ink"
        >
          Close
        </button>
      </div>
    </div>
  );
}