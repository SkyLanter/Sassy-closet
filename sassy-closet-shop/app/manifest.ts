import type { MetadataRoute } from "next";
import { HOME_DESCRIPTION } from "@/lib/trust-copy";
import { SITE } from "@/lib/site";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: SITE.name,
    short_name: SITE.name,
    description: HOME_DESCRIPTION,
    start_url: "/",
    display: "standalone",
    background_color: "#fdece6",
    theme_color: "#fdece6",
    icons: [{ src: "/icon.svg", sizes: "any", type: "image/svg+xml", purpose: "any" }],
  };
}
