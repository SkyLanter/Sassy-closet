"use client";

import { useState } from "react";
import { useCatalogMediaVersion } from "@/components/catalog-media-version";
import { MaMark } from "@/components/ma-mark";
import { cacheBustMediaSrc, shopCoverSrc } from "@/lib/catalog-sha";
import { coverSrc } from "@/lib/product-media";
import type { ShopLook } from "@/lib/shop-look";

export function ProductImage({
  product,
  src,
  priority = false,
  className,
  named = true,
  coverFallback = true,
}: {
  product: ShopLook;
  src?: string;
  priority?: boolean;
  className?: string;
  named?: boolean;
  coverFallback?: boolean;
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
      priority={priority}
      className={className}
      named={named}
    />
  );
}

function ProductImageFrame({
  product,
  resolved,
  priority,
  className,
  named,
}: {
  product: ShopLook;
  resolved: string | undefined;
  priority: boolean;
  className?: string;
  named: boolean;
}) {
  const [failed, setFailed] = useState(false);
  const showImage = Boolean(resolved) && !failed;

  return (
    <div
      className={`relative overflow-hidden bg-[#f3f1ee] ${className ?? "aspect-[3/4]"}`}
      style={named ? { viewTransitionName: `product-${product.ma}` } : undefined}
    >
      <div className="shimmer pointer-events-none absolute inset-0 z-[2]" aria-hidden />
      {showImage && resolved ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={resolved}
          alt=""
          draggable={false}
          className="relative z-[1] h-full w-full select-none object-cover motion-safe:transition-transform motion-safe:duration-[800ms] motion-safe:ease-out motion-safe:hover-hover:group-hover:scale-[1.08]"
          sizes="(max-width: 640px) 50vw, (max-width: 1280px) 25vw, 20vw"
          decoding="async"
          loading={priority ? "eager" : "lazy"}
          fetchPriority={priority ? "high" : "auto"}
          onError={() => {
            setFailed(true);
          }}
        />
      ) : (
        <PlaceholderTile ma={product.ma} letter={product.type} decorative />
      )}
    </div>
  );
}

export function PlaceholderTile({
  ma,
  letter,
  decorative = false,
}: {
  ma: string;
  letter: string;
  decorative?: boolean;
}) {
  return (
    <div
      className="relative z-0 flex h-full w-full flex-col items-center justify-center bg-[#f4f1ec]"
      aria-hidden={decorative || undefined}
    >
      <span className="font-display text-6xl font-medium leading-[1.08] text-gold/80">{letter}</span>
      <span className="mt-2 text-gold-deep">
        <MaMark ma={ma} className="text-[11px] tracking-[0.16em]" />
      </span>
    </div>
  );
}
