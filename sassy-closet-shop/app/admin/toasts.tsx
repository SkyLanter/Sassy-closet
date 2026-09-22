"use client";

export type ToastTone = "ok" | "error";

export type AdminToast = {
  id: string;
  tone: ToastTone;
  text: string;
};

const TOAST_KEY = "sassy-closet-admin-toast";

export function persistAdminToast(tone: ToastTone, text: string): void {
  try {
    sessionStorage.setItem(TOAST_KEY, JSON.stringify({ tone, text, at: Date.now() }));
  } catch {
    // private mode / blocked storage
  }
}

export function takePersistedAdminToast(): { tone: ToastTone; text: string } | null {
  try {
    const raw = sessionStorage.getItem(TOAST_KEY);
    if (!raw) {
      return null;
    }
    sessionStorage.removeItem(TOAST_KEY);
    const parsed = JSON.parse(raw) as { tone?: string; text?: string; at?: number };
    if ((parsed.tone !== "ok" && parsed.tone !== "error") || typeof parsed.text !== "string") {
      return null;
    }
    if (typeof parsed.at === "number" && Date.now() - parsed.at > 20_000) {
      return null;
    }
    return { tone: parsed.tone, text: parsed.text };
  } catch {
    return null;
  }
}

export function ToastHost({
  toasts,
  onDismiss,
}: {
  toasts: AdminToast[];
  onDismiss: (id: string) => void;
}) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div
      className="pointer-events-none fixed right-4 z-[90] flex w-[min(100%-2rem,22rem)] flex-col gap-2"
      style={{ top: "max(1rem, env(safe-area-inset-top, 0px))" }}
      aria-live="polite"
      aria-relevant="additions"
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          role={toast.tone === "error" ? "alert" : "status"}
          className={`pointer-events-auto rounded-xl border px-4 py-3 text-sm shadow-lg ${
            toast.tone === "error"
              ? "border-gold-deep/40 bg-paper text-gold-deep"
              : "border-ink/10 bg-ink text-paper"
          }`}
        >
          <div className="flex items-start justify-between gap-3">
            <p>{toast.text}</p>
            <button
              type="button"
              className={`inline-flex min-h-8 shrink-0 touch-manipulation items-center text-xs uppercase tracking-[0.12em] ${
                toast.tone === "error" ? "text-gold-deep" : "text-paper/70"
              }`}
              onClick={() => onDismiss(toast.id)}
            >
              Close
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
