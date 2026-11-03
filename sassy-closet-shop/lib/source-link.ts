const TAOBAO_HOSTS = new Set(["e.tb.cn", "tb.cn", "m.tb.cn", "taobao.com"]);

function isTaobaoHost(host: string): boolean {
  const hostname = host.toLowerCase();
  if (TAOBAO_HOSTS.has(hostname)) {
    return true;
  }
  return hostname.endsWith(".taobao.com") || hostname.endsWith(".tb.cn");
}

/** Keep a Taobao source URL if Boss pasted one. Never invent a link. */
export function parseSourceLink(value: unknown, ma?: string): string | null {
  if (value === undefined || value === null) {
    return null;
  }
  if (typeof value !== "string") {
    throw new Error(ma ? `Mã ${ma} sourceLink must be a string` : "sourceLink must be a string");
  }
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  let url: URL;
  try {
    url = new URL(trimmed);
  } catch {
    throw new Error(
      ma ? `Mã ${ma} sourceLink is not a valid URL` : "sourceLink is not a valid URL",
    );
  }
  if (url.protocol !== "https:" && url.protocol !== "http:") {
    throw new Error(
      ma ? `Mã ${ma} sourceLink must be http(s)` : "sourceLink must be http(s)",
    );
  }
  if (!isTaobaoHost(url.hostname)) {
    throw new Error(
      ma
        ? `Mã ${ma} sourceLink must be a Taobao link (e.tb.cn). Do not invent links.`
        : "sourceLink must be a Taobao link (e.tb.cn). Do not invent links.",
    );
  }
  return url.toString();
}
