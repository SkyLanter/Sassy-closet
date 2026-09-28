"use client";

import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "framer-motion";
import { LookPhoto } from "@/components/look-photo";

const MAX_SCALE = 4;
const TAP_SCALE = 2.4;

export function ZoomLayer({
  src,
  alt,
  onClose,
}: {
  src: string;
  alt: string;
  onClose: () => void;
}) {
  const reduced = useReducedMotion();
  const closeRef = useRef<HTMLButtonElement>(null);
  const surfaceRef = useRef<HTMLDivElement>(null);
  const scaleRef = useRef(1);
  const [scale, setScale] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [pinching, setPinching] = useState(false);

  function setScaleTo(next: number) {
    const clamped = Math.min(MAX_SCALE, Math.max(1, next));
    scaleRef.current = clamped;
    setScale(clamped);
    if (clamped === 1) {
      setPan({ x: 0, y: 0 });
    }
  }

  useEffect(() => {
    closeRef.current?.focus();
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape" || event.key === "Enter") {
        if (event.key === "Enter") {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        onClose();
      }
    }
    document.addEventListener("keydown", onKey, true);
    return () => document.removeEventListener("keydown", onKey, true);
  }, [onClose]);

  useEffect(() => {
    const el = surfaceRef.current;
    if (!el) {
      return;
    }
    const pointers = new Map<number, { x: number; y: number }>();
    let pinch: { dist: number; scale: number } | null = null;
    let last = { x: 0, y: 0 };
    let dragged = false;
    let lastTap = 0;

    function distance(): number {
      const pts = [...pointers.values()];
      if (pts.length < 2) {
        return 0;
      }
      return Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
    }

    function down(event: PointerEvent) {
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      last = { x: event.clientX, y: event.clientY };
      dragged = false;
      if (pointers.size === 2) {
        pinch = { dist: distance(), scale: scaleRef.current };
        setPinching(true);
      }
    }

    function move(event: PointerEvent) {
      const prev = pointers.get(event.pointerId);
      if (!prev) {
        return;
      }
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.size >= 2 && pinch && pinch.dist > 0) {
        event.preventDefault();
        const next = Math.min(MAX_SCALE, Math.max(1, pinch.scale * (distance() / pinch.dist)));
        scaleRef.current = next;
        setScale(next);
        if (next === 1) {
          setPan({ x: 0, y: 0 });
        }
        return;
      }
      if (pointers.size === 1 && scaleRef.current > 1) {
        const dx = event.clientX - last.x;
        const dy = event.clientY - last.y;
        if (Math.hypot(dx, dy) > 3) {
          dragged = true;
        }
        event.preventDefault();
        setPan((current) => ({ x: current.x + dx, y: current.y + dy }));
      }
      last = { x: event.clientX, y: event.clientY };
    }

    function up(event: PointerEvent) {
      pointers.delete(event.pointerId);
      if (pointers.size < 2) {
        pinch = null;
        setPinching(false);
      }
      if (pointers.size !== 0 || dragged) {
        return;
      }
      const now = performance.now();
      if (now - lastTap < 280) {
        const next = scaleRef.current > 1 ? 1 : TAP_SCALE;
        scaleRef.current = next;
        setScale(next);
        if (next === 1) {
          setPan({ x: 0, y: 0 });
        }
        lastTap = 0;
        return;
      }
      lastTap = now;
    }

    el.addEventListener("pointerdown", down);
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerup", up);
    el.addEventListener("pointercancel", up);
    return () => {
      el.removeEventListener("pointerdown", down);
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerup", up);
      el.removeEventListener("pointercancel", up);
    };
  }, []);

  const transition = reduced || pinching ? "none" : "transform 180ms cubic-bezier(0.23, 1, 0.32, 1)";

  return (
    <div
      className="absolute inset-0 z-30 flex flex-col bg-paper"
      role="dialog"
      aria-modal="true"
      aria-label={alt}
      data-testid="photo-zoom"
    >
      <div className="flex items-center justify-end gap-2 px-1 pt-1">
        <button
          type="button"
          onClick={() => setScaleTo(scale > 1 ? 1 : TAP_SCALE)}
          className="sc-press inline-flex min-h-11 touch-manipulation items-center rounded-full border border-gold/45 px-4 text-[11px] uppercase tracking-[0.16em] text-ink"
          aria-pressed={scale > 1}
        >
          {scale > 1 ? "Thu nhỏ" : "Phóng to"}
        </button>
        <button
          ref={closeRef}
          type="button"
          onClick={onClose}
          aria-label="Đóng phóng to · Close zoom"
          className="sc-press flex h-11 w-11 touch-manipulation items-center justify-center rounded-full border border-gold/45 text-ink"
        >
          <span aria-hidden>✕</span>
        </button>
      </div>
      <div ref={surfaceRef} className="relative min-h-0 flex-1 overflow-hidden" style={{ touchAction: "none" }}>
        <div
          className="flex h-full w-full items-center justify-center"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${scale})`,
            transition,
          }}
        >
          <LookPhoto
            src={src}
            alt={alt}
            sizes="100vw"
            fill={false}
            priority
            className="h-auto max-h-[78dvh] w-full select-none object-contain"
          />
        </div>
      </div>
    </div>
  );
}
