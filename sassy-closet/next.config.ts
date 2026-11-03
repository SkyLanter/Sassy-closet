import type { NextConfig } from "next";
import { INTAKE_DIRECT_LINK_HEADERS, INTAKE_DIRECT_LINK_SOURCES } from "./lib/intake-direct-link-headers";

const directLinkHeaders = Object.entries(INTAKE_DIRECT_LINK_HEADERS).map(([key, value]) => ({
  key,
  value,
}));

const nextConfig: NextConfig = {
  poweredByHeader: false,
  async headers() {
    return INTAKE_DIRECT_LINK_SOURCES.map((source) => ({
      source,
      headers: directLinkHeaders,
    }));
  },
};

export default nextConfig;
