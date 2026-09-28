"use client";

import Image from "next/image";
import { BLUSH_BLUR } from "@/lib/image-placeholder";

export function LookPhoto({
  src,
  alt,
  sizes,
  priority = false,
  className,
  onError,
  fill = true,
  width = 1200,
  height = 1600,
}: {
  src: string;
  alt: string;
  sizes: string;
  priority?: boolean;
  className?: string;
  onError?: () => void;
  fill?: boolean;
  width?: number;
  height?: number;
}) {
  if (fill) {
    return (
      <Image
        src={src}
        alt={alt}
        fill
        sizes={sizes}
        priority={priority}
        placeholder="blur"
        blurDataURL={BLUSH_BLUR}
        draggable={false}
        className={className}
        onError={onError}
      />
    );
  }

  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      sizes={sizes}
      priority={priority}
      placeholder="blur"
      blurDataURL={BLUSH_BLUR}
      draggable={false}
      className={className}
      onError={onError}
    />
  );
}
