"use client";

import { useEffect, useRef, useState } from "react";

export type ToastTone = "ok" | "danger" | "info";

export type ToastItem = {
  id: number;
  text: string;
  tone: ToastTone;
};

const TOAST_MS = 5000;

export function ToastStack({
  toasts,
  onDismiss,
}: {
  toasts: ToastItem[];
  onDismiss: (id: number) => void;
}) {
  const visible = toasts.slice(-4);
  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-[max(1rem,env(safe-area-inset-bottom))] z-[80] flex flex-col items-center gap-2 px-4">
      {visible.map((toast) => (
        <ToastLine key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

function ToastLine({
  toast,
  onDismiss,
}: {
  toast: ToastItem;
  onDismiss: (id: number) => void;
}) {
  const [paused, setPaused] = useState(false);
  const started = useRef(Date.now());
  const left = useRef(TOAST_MS);

  useEffect(() => {
    if (paused) {
      left.current = Math.max(0, left.current - (Date.now() - started.current));
      return;
    }
    started.current = Date.now();
    const timer = window.setTimeout(() => onDismiss(toast.id), left.current);
    return () => window.clearTimeout(timer);
  }, [paused, onDismiss, toast.id]);

  const tone =
    toast.tone === "danger"
      ? "bg-[#fde8e6] text-[#9b2c2c]"
      : toast.tone === "info"
        ? "bg-[#e7f1f6] text-[#1f5670]"
        : "bg-[#e7f4ec] text-[#246044]";

  return (
    <p
      role="status"
      className={`pointer-events-auto max-w-sm rounded-2xl px-4 py-3 text-[13.5px] shadow-sm ring-1 ring-black/5 ${tone}`}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      {toast.text}
    </p>
  );
}

export function ConfirmDialog({
  title,
  body,
  confirmLabel,
  pending,
  danger,
  onCancel,
  onConfirm,
}: {
  title: string;
  body: string;
  confirmLabel: string;
  pending: boolean;
  danger?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const cancelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    cancelRef.current?.focus();
  }, []);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onCancel();
      }
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return (
    <div
      className="fixed inset-0 z-[70] flex items-end justify-center bg-[#2a1d22]/35 p-0 sm:items-center sm:p-6"
      role="presentation"
      onClick={onCancel}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        className="w-full max-w-md rounded-t-3xl bg-[#fffaf8] p-5 shadow-sm ring-1 ring-[#eadfdc] sm:rounded-3xl"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 id="confirm-title" className="text-[21px] leading-tight text-[#3c2a2e]">
          {title}
        </h2>
        <p className="mt-2 text-[13.5px] leading-relaxed text-[#7d5360]">{body}</p>
        <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button
            ref={cancelRef}
            type="button"
            className="inline-flex min-h-11 items-center justify-center rounded-full px-4 text-sm font-semibold text-[#5c3d48] ring-1 ring-[#eadfdc]"
            onClick={onCancel}
          >
            Huỷ
          </button>
          <button
            type="button"
            disabled={pending}
            className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-full px-4 text-sm font-semibold text-white disabled:opacity-60 ${
              danger ? "bg-[#9b2c2c]" : "bg-primary"
            }`}
            onClick={onConfirm}
          >
            {pending ? <span className="adm-spin" aria-hidden /> : null}
            {pending ? "Đang lưu…" : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
