import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  images: {
    formats: ["image/avif", "image/webp"],
    deviceSizes: [375, 430, 640, 768, 1024, 1280, 1536],
    imageSizes: [64, 72, 96, 128, 256, 384],
    // Catalog covers are cache-busted with ?v=. A custom pathname (not the
    // default "**" + empty search) is what lets next/image accept that query.
    localPatterns: [
      { pathname: "/products/**" },
      { pathname: "/uploads/**" },
      { pathname: "/editorial/**" },
    ],
    remotePatterns: [
      { protocol: "https", hostname: "**.public.blob.vercel-storage.com" },
      { protocol: "https", hostname: "**.blob.vercel-storage.com" },
    ],
  },
  experimental: {
    serverActions: {
      bodySizeLimit: "8mb",
    },
  },
  async headers() {
    const noStore = [
      { key: "Cache-Control", value: "private, no-store, no-cache, max-age=0, must-revalidate" },
      { key: "Pragma", value: "no-cache" },
    ];
    return [
      { source: "/", headers: noStore },
      { source: "/m/:path*", headers: noStore },
      { source: "/c/:path*", headers: noStore },
      { source: "/how-to-buy", headers: noStore },
      { source: "/meetup-ship", headers: noStore },
      { source: "/admin/:path*", headers: noStore },
      { source: "/admin", headers: noStore },
      { source: "/api/admin/:path*", headers: noStore },
      { source: "/products/:path*", headers: noStore },
    ];
  },
};

export default nextConfig;
