/**
 * Hosts next/image may optimize. Kept in one place so the config and the
 * catalog test cannot drift. Patterns follow Next's picomatch host rules:
 * `**.example.com` matches a subdomain, not the apex.
 *
 * Live catalog (62 mãs, 2026-09-28): *.public.blob.vercel-storage.com,
 * img.alicdn.com, litter.catbox.moe. `**.alicdn.com` also covers gw.alicdn.com
 * and the other Alicdn CDNs. files.catbox.moe is the sibling of litter.
 */
export const SHOP_REMOTE_IMAGE_PATTERNS: ReadonlyArray<{
  protocol: "https";
  hostname: string;
}> = [
  { protocol: "https", hostname: "**.public.blob.vercel-storage.com" },
  { protocol: "https", hostname: "**.blob.vercel-storage.com" },
  { protocol: "https", hostname: "**.alicdn.com" },
  { protocol: "https", hostname: "litter.catbox.moe" },
  { protocol: "https", hostname: "files.catbox.moe" },
];

function hostMatches(pattern: string, hostname: string): boolean {
  if (pattern.startsWith("**.")) {
    return hostname.endsWith(`.${pattern.slice(3)}`);
  }
  if (pattern.startsWith("*.")) {
    const suffix = pattern.slice(2);
    if (!hostname.endsWith(`.${suffix}`)) {
      return false;
    }
    const prefix = hostname.slice(0, -(suffix.length + 1));
    return prefix.length > 0 && !prefix.includes(".");
  }
  return hostname === pattern;
}

/** True when next/image remotePatterns will accept this URL. Local paths are not remote. */
export function remoteImageAllowed(src: string): boolean {
  let url: URL;
  try {
    url = new URL(src);
  } catch {
    return false;
  }
  if (url.protocol !== "https:") {
    return false;
  }
  const hostname = url.hostname.toLowerCase();
  return SHOP_REMOTE_IMAGE_PATTERNS.some(
    (pattern) => pattern.protocol === "https" && hostMatches(pattern.hostname, hostname),
  );
}

/** Optimizer for allowed remote URLs and same-origin paths. Anything else uses a plain img. */
export function shouldOptimizeImage(src: string): boolean {
  if (src.startsWith("/") && !src.startsWith("//")) {
    return true;
  }
  return remoteImageAllowed(src);
}

export function hostnameOfImageSrc(src: string): string | null {
  if (!src.startsWith("http://") && !src.startsWith("https://")) {
    return null;
  }
  try {
    return new URL(src).hostname.toLowerCase();
  } catch {
    return null;
  }
}
