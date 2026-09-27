import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
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
    const adminHeaders = [
      ...noStore,
      { key: "X-Robots-Tag", value: "noindex, nofollow" },
    ];
    return [
      { source: "/", headers: noStore },
      { source: "/m/:path*", headers: noStore },
      { source: "/c/:path*", headers: noStore },
      { source: "/how-to-buy", headers: noStore },
      { source: "/meetup-ship", headers: noStore },
      { source: "/admin/:path*", headers: adminHeaders },
      { source: "/admin", headers: adminHeaders },
      { source: "/api/admin/:path*", headers: adminHeaders },
      { source: "/products/:path*", headers: noStore },
    ];
  },
};

export default nextConfig;
