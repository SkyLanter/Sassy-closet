"use client";

import { useLayoutEffect, useRef, useState } from "react";
import Image from "next/image";
import { BLUSH_BLUR } from "@/lib/image-placeholder";
import { shouldOptimizeImage } from "@/lib/image-hosts";

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
}) {
  const imagePriority = fetchPriority ?? "auto";
  if (!shouldOptimizeImage(src)) {
    return (
      <NativeLookPhoto
        src={src}
        alt={alt}
        sizes={sizes}
        priority={priority}
        fetchPriority={imagePriority}
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
    if (priority || !img || (img.complete && img.naturalWidth > 0)) {
      setPending(false);
      return;
    }
    setPending(true);
  }, [priority, src]);

  return (
    <img
      ref={imgRef}
      src={src}
      alt={alt}
      width={fill ? undefined : width}
      height={fill ? undefined : height}
      sizes={sizes}
      draggable={false}
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
