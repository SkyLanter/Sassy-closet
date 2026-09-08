"use client";

import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";

export function PhotoLightbox({
  src,
  alt = "",
  onClose,
}: {
  src: string | null;
  alt?: string;
  onClose: () => void;
}) {
  const [mounted, setMounted] = useState(false);
  const closeRef = useRef<HTMLButtonElement>(null);
  const onCloseRef = useRef(onClose);
  const titleId = useId();
  onCloseRef.current = onClose;

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!src) return;
    const previous = document.activeElement as HTMLElement | null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();

    function onKey(event: KeyboardEvent) {
      if (event.key !== "Escape") return;
      event.preventDefault();
      event.stopPropagation();
      onCloseRef.current();
    }

    document.addEventListener("keydown", onKey, true);
    return () => {
      document.removeEventListener("keydown", onKey, true);
      document.body.style.overflow = overflow;
      previous?.focus?.();
    };
  }, [src]);

  if (!src || !mounted) return null;

  return createPortal(
    <div
      data-testid="photo-lightbox"
      className="fixed inset-0 z-[80] flex items-center justify-center bg-rose-950/50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      onClick={onClose}
    >
      <p id={titleId} className="sr-only">
        Ảnh lớn
      </p>
      <button
        ref={closeRef}
        type="button"
        data-testid="photo-lightbox-close"
        aria-label="Đóng"
        className="absolute right-3 top-3 z-10 flex h-11 w-11 items-center justify-center rounded-full bg-white/95 text-lg font-bold text-rose-700 shadow-md ring-1 ring-rose-100 sm:right-5 sm:top-5"
        onClick={(event) => {
          event.stopPropagation();
          onClose();
        }}
      >
        ✕
      </button>
      <img
        data-testid="photo-lightbox-image"
        src={src}
        alt={alt}
        className="max-h-[88dvh] max-w-full rounded-3xl object-contain shadow-2xl ring-4 ring-white/70"
        onClick={(event) => event.stopPropagation()}
      />
    </div>,
    document.body,
  );
}
