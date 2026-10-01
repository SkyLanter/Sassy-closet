"use client";

import { useLayoutEffect, useRef, useState } from "react";
import Image from "next/image";
import { BLUSH_BLUR } from "@/lib/image-placeholder";
import { shouldOptimizeImage } from "@/lib/image-hosts";
import { lookCardFetchPriority } from "@/lib/look-card-photo";

export function LookPhoto({
  src,
  alt,
  sizes,
  priority = false,
  fetchPriority,
  className,
  onError,
  fill = true,
  width = 1200,
  height = 1600,
  fadeIn = false,
}: {
  src: string;
  alt: string;
  sizes: string;
  priority?: boolean;
  fetchPriority?: "high" | "low" | "auto";
  className?: string;
  onError?: () => void;
  fill?: boolean;
  width?: number;
  height?: number;
  /** Card covers only. Fades the photo in over the blush plate. Does not gate the card shell. */
  fadeIn?: boolean;
}) {
  const imagePriority = lookCardFetchPriority(priority, fetchPriority);
  if (!shouldOptimizeImage(src)) {
    return (
      <NativeLookPhoto
        src={src}
        alt={alt}
        sizes={sizes}
        priority={priority}
        fetchPriority={imagePriority}
        fadeIn={fadeIn}
        className={
          fill ? `absolute inset-0 h-full w-full ${className ?? ""}` : className
        }
        fill={fill}
        width={width}
        height={height}
        onError={onError}
      />
    );
  }

  if (fill) {
    return (
      <Image
        src={src}
        alt={alt}
        fill
        sizes={sizes}
        priority={priority}
        fetchPriority={imagePriority}
        decoding="async"
        loading={priority ? "eager" : "lazy"}
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
      fetchPriority={imagePriority}
      decoding="async"
      loading={priority ? "eager" : "lazy"}
      placeholder="blur"
      blurDataURL={BLUSH_BLUR}
      draggable={false}
      className={className}
      onError={onError}
    />
  );
}

function NativeLookPhoto({
  src,
  alt,
  sizes,
  priority,
  fetchPriority,
  fadeIn,
  className,
  fill,
  width,
  height,
  onError,
}: {
  src: string;
  alt: string;
  sizes: string;
  priority: boolean;
  fetchPriority: "high" | "low" | "auto";
  fadeIn: boolean;
  className?: string;
  fill: boolean;
  width: number;
  height: number;
  onError?: () => void;
}) {
  const imgRef = useRef<HTMLImageElement>(null);
  const [pending, setPending] = useState(false);

  useLayoutEffect(() => {
    const img = imgRef.current;
    const cached = Boolean(img && img.complete && img.naturalWidth > 0);
    if (cached || !img || (!fadeIn && priority)) {
      setPending(false);
      return;
    }
    setPending(true);
  }, [fadeIn, priority, src]);

  return (
    <img
      ref={imgRef}
      src={src}
      alt={alt}
      width={fill ? undefined : width}
      height={fill ? undefined : height}
      sizes={sizes}
      draggable={false}
      decoding="async"
      loading={priority ? "eager" : "lazy"}
      fetchPriority={fetchPriority}
      data-loaded={pending ? "false" : "true"}
      onLoad={() => {
        setPending(false);
      }}
      onError={onError}
      className={`sc-photo ${className ?? ""}`}
    />
  );
}
