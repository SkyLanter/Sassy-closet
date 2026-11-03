import type { NextConfig } from "next";
import path from "node:path";
import { SHOP_REMOTE_IMAGE_PATTERNS } from "./lib/image-hosts";
import { PRIVATE_ROBOTS_TAG } from "./lib/private-robots";

const nextConfig: NextConfig = {
  turbopack: {
    // Held mãs live in repo-root data/held.json, outside this app directory.
    root: path.join(import.meta.dirname, ".."),
  },
  allowedDevOrigins: ["127.0.0.1"],
  images: {
    // WebP only. AVIF plus WebP asks the optimizer for two files per size.
    // Remote catalog hosts are a plain <img> (shouldOptimizeImage): each
    // catalog write changes ?v= and would otherwise re-process every photo.
    formats: ["image/webp"],
    deviceSizes: [375, 430, 640, 768, 1024, 1280, 1536],
    imageSizes: [64, 72, 96, 128, 256, 384],
    // Catalog covers are cache-busted with ?v=. A custom pathname (not the
    // default "**" + empty search) is what lets next/image accept that query.
    localPatterns: [
      { pathname: "/products/**" },
      { pathname: "/uploads/**" },
      { pathname: "/editorial/**" },
    ],
    remotePatterns: SHOP_REMOTE_IMAGE_PATTERNS.map((pattern) => ({ ...pattern })),
  },
  experimental: {
    serverActions: {
      bodySizeLimit: "8mb",
    },
  },
  outputFileTracingIncludes: {
    "/opengraph-image": ["./assets/og-fonts/**/*", "./public/products/**/*"],
    "/share/m/[ma]": ["./assets/og-fonts/**/*", "./public/products/**/*"],
    "/share/c/[slug]": ["./assets/og-fonts/**/*", "./public/products/**/*"],
  },
  async headers() {
    const noStore = [
      { key: "Cache-Control", value: "private, no-store, no-cache, max-age=0, must-revalidate" },
      { key: "Pragma", value: "no-cache" },
    ];
    const privateSurface = [
      ...noStore,
      { key: "X-Robots-Tag", value: PRIVATE_ROBOTS_TAG },
    ];
    return [
      { source: "/", headers: noStore },
      { source: "/m/:path*", headers: noStore },
      { source: "/c/:path*", headers: noStore },
      { source: "/how-to-buy", headers: noStore },
      { source: "/meetup-ship", headers: noStore },
      { source: "/admin", headers: privateSurface },
      { source: "/admin/:path*", headers: privateSurface },
      { source: "/api", headers: privateSurface },
      { source: "/api/:path*", headers: privateSurface },
      { source: "/products/:path*", headers: noStore },
    ];
  },
};

export default nextConfig;
