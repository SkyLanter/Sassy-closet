"use client";

import { useState } from "react";
import { useCatalogMediaVersion } from "@/components/catalog-media-version";
import { LookPhoto } from "@/components/look-photo";
import { MaMark } from "@/components/ma-mark";
import { cacheBustMediaSrc, shopCoverSrc } from "@/lib/catalog-sha";
import { BLUSH_BLUR } from "@/lib/image-placeholder";
import { LOOK_GRID_SIZES } from "@/lib/look-card-photo";
import { coverSrc } from "@/lib/product-media";
import { SITE } from "@/lib/site";
import type { ShopLook } from "@/lib/shop-look";

export function ProductImage({
  product,
  src,
  alt,
  priority = false,
  className,
  named = true,
  coverFallback = true,
  sizes = LOOK_GRID_SIZES,
}: {
  product: ShopLook;
  src?: string;
  alt: string;
  priority?: boolean;
  className?: string;
  named?: boolean;
  coverFallback?: boolean;
  sizes?: string;
}) {
  const version = useCatalogMediaVersion();
  const fallback = coverFallback
    ? version
      ? shopCoverSrc(product.ma, version)
      : coverSrc(product)
    : undefined;
  const raw = src ?? fallback;
  const resolved = raw && version ? cacheBustMediaSrc(raw, version) : raw;

  return (
    <ProductImageFrame
      key={resolved ?? "none"}
      product={product}
      resolved={resolved}
      alt={alt}
      priority={priority}
      className={className}
      named={named}
      sizes={sizes}
    />
  );
}

function ProductImageFrame({
  product,
  resolved,
  alt,
  priority,
  className,
  named,
  sizes,
}: {
  product: ShopLook;
  resolved: string | undefined;
  alt: string;
  priority: boolean;
  className?: string;
  named: boolean;
  sizes: string;
}) {
  const [failed, setFailed] = useState(false);
  const showImage = Boolean(resolved) && !failed;

  return (
    <div
      className={`relative overflow-hidden bg-[#f3f1ee] ${className ?? "aspect-[3/4]"}`}
      style={{
        backgroundImage: `url("${BLUSH_BLUR}")`,
        backgroundPosition: "center top",
        backgroundSize: "cover",
        ...(named ? { viewTransitionName: `product-${product.ma}` } : {}),
      }}
    >
      <div className="shimmer pointer-events-none absolute inset-0 z-[2]" aria-hidden />
      {showImage && resolved ? (
        <LookPhoto
          src={resolved}
          alt={alt}
          sizes={sizes}
          priority={priority}
          fadeIn
          onError={() => {
            setFailed(true);
          }}
          className="sc-card-photo object-cover object-top select-none motion-safe:transition-transform motion-safe:duration-150 motion-safe:ease-[cubic-bezier(0.23,1,0.32,1)] motion-safe:hover-hover:group-hover:scale-[1.03]"
        />
      ) : (
        <PlaceholderTile ma={product.ma} letter={product.type} decorative />
      )}
    </div>
  );
}

export function FallibleLookPhoto({
  src,
  alt,
  sizes,
  priority = false,
  fetchPriority,
  className,
  fill = true,
  width,
  height,
  ma,
  letter,
  compact = false,
}: {
  src: string;
  alt: string;
  sizes: string;
  priority?: boolean;
  fetchPriority?: "high" | "low" | "auto";
  className?: string;
  fill?: boolean;
  width?: number;
  height?: number;
  ma: string;
  letter: string;
  compact?: boolean;
}) {
  const [failedSrc, setFailedSrc] = useState<string | null>(null);
  if (failedSrc === src) {
    return <PlaceholderTile ma={ma} letter={letter} decorative compact={compact} />;
  }
  return (
    <LookPhoto
      src={src}
      alt={alt}
      sizes={sizes}
      priority={priority}
      fetchPriority={fetchPriority}
      className={className}
      fill={fill}
      width={width}
      height={height}
      onError={() => {
        setFailedSrc(src);
      }}
    />
  );
}

export function PlaceholderTile({
  ma,
  letter,
  decorative = false,
  compact = false,
}: {
  ma: string;
  letter: string;
  decorative?: boolean;
  compact?: boolean;
}) {
  return (
    <div
      className="sc-photo-fallback relative z-0 flex h-full w-full select-none flex-col items-center justify-center bg-canvas px-2 text-center"
      aria-hidden={decorative || undefined}
      data-fallback-letter={letter}
    >
      <span className={`font-display font-medium leading-[1.12] tracking-[0.02em] text-ink ${compact ? "text-[11px]" : "text-[15px]"}`}>
        {SITE.name}
      </span>
      <span className="mt-1 text-muted">
        <MaMark ma={ma} className="text-[11px] tracking-[0.16em]" />
      </span>
    </div>
  );
}
