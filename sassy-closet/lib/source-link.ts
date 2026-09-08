const HTTP_URL_RE =
  /https?:\/\/[A-Za-z0-9][-A-Za-z0-9._]*(?::\d{1,5})?(?:\/[-A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%]*)?/gi;

const TRAILING_PUNCT_RE = /[.,;:!?)\]}>]+$/;

const PREFERRED_HOST_RE = [/(^|\.)e\.tb\.cn$/i, /(^|\.)tb\.cn$/i, /(^|\.)taobao\.com$/i, /(^|\.)tmall\.com$/i];

export function normalizeSourceLink(raw: string): string {
  const text = String(raw ?? "")
    .replace(/\u00a0/g, " ")
    .trim();
  if (!text) return "";

  const urls = extractHttpUrls(text);
  if (urls.length === 0) return "";

  const preferred = urls.filter(isPreferredShopUrl);
  return preferred[0] ?? urls[0] ?? "";
}

function extractHttpUrls(text: string): string[] {
  const found: string[] = [];
  const re = new RegExp(HTTP_URL_RE.source, HTTP_URL_RE.flags);
  let match: RegExpExecArray | null;
  while ((match = re.exec(text))) {
    const cleaned = match[0].replace(TRAILING_PUNCT_RE, "");
    if (cleaned) found.push(cleaned);
  }
  return found;
}

function isPreferredShopUrl(url: string): boolean {
  try {
    const host = new URL(url).hostname.toLowerCase();
    return PREFERRED_HOST_RE.some((pattern) => pattern.test(host));
  } catch {
    return false;
  }
}
