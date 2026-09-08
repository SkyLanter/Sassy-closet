"use client";

import { useState } from "react";
import { PhotoLightbox } from "@/components/PhotoLightbox";
import { assertNever } from "@/lib/kinds";
import { FIND_CARD_THUMB_LIMIT, photoSrc, visiblePhotoPaths } from "@/lib/photos";

type PhotoLayout = "row" | "grid";

export function PhotoThumbs({
  photos,
  max,
  layout = "grid",
  testId,
  emptyTestId,
  moreTestId,
  thumbTestIdPrefix,
  className,
}: {
  photos: string[];
  max?: number;
  layout?: PhotoLayout;
  testId?: string;
  emptyTestId?: string;
  moreTestId?: string;
  thumbTestIdPrefix?: string;
  className?: string;
}) {
  const [openSrc, setOpenSrc] = useState<string | null>(null);
  const limit = max ?? (layout === "row" ? FIND_CARD_THUMB_LIMIT : Number.POSITIVE_INFINITY);
  const { shown, extra } = visiblePhotoPaths(photos, limit);

  if (shown.length === 0) {
    return emptyTestId ? (
      <p data-testid={emptyTestId} className="mt-4 text-center text-xs text-rose-700/70">
        —
      </p>
    ) : null;
  }

  return (
    <>
      <div data-testid={testId} className={`${layoutClass(layout)} ${className ?? "mt-4"}`}>
        {shown.map((rel, index) => (
          <Thumb
            key={`${rel}-${index}`}
            src={photoSrc(rel)}
            extra={index === shown.length - 1 ? extra : 0}
            testId={thumbTestIdPrefix ? `${thumbTestIdPrefix}-${index}` : undefined}
            moreTestId={moreTestId}
            onOpen={() => setOpenSrc(photoSrc(rel))}
          />
        ))}
      </div>
      <PhotoLightbox src={openSrc} onClose={() => setOpenSrc(null)} />
    </>
  );
}

function layoutClass(layout: PhotoLayout): string {
  switch (layout) {
    case "row":
      return "grid grid-cols-3 grid-rows-1 gap-2";
    case "grid":
      return "grid grid-cols-3 gap-2";
    default: {
      const _never: never = layout;
      return assertNever(_never, "Unknown photo layout");
    }
  }
}

function Thumb({
  src,
  extra,
  testId,
  moreTestId,
  onOpen,
}: {
  src: string;
  extra: number;
  testId?: string;
  moreTestId?: string;
  onOpen: () => void;
}) {
  const [ok, setOk] = useState(true);
  if (!src || !ok) return null;
  const label = extra > 0 ? `Xem ảnh, còn ${extra} ảnh nữa` : "Xem ảnh lớn";
  return (
    <button
      type="button"
      data-testid={testId}
      aria-label={label}
      className="relative min-w-0 overflow-hidden rounded-xl"
      onClick={onOpen}
    >
      <img
        src={src}
        alt=""
        className="h-24 w-full object-cover"
        onError={() => setOk(false)}
      />
      {extra > 0 ? (
        <span
          data-testid={moreTestId}
          className="absolute inset-0 flex items-center justify-center rounded-xl bg-rose-950/40 text-sm font-bold text-white"
        >
          +{extra}
        </span>
      ) : null}
    </button>
  );
}
