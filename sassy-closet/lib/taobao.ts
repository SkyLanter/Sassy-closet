/**
 * Best-effort server-side Taobao listing parser.
 *
 * All helpers here are pure (no network) so they can be unit tested.
 * Taobao usually blocks automated fetches, so every consumer must
 * degrade gracefully and NEVER invent data when the fetch fails.
 */
import { normalizeSourceLink } from "./source-link";

export type TaobaoSkuAxis = {
  /** Seller's axis name, Chinese as shown by the seller, e.g. "颜色分类". */
  name: string;
  /** Seller's option values, Chinese as shown by the seller. */
  values: string[];
};

export type TaobaoItem = {
  itemId: string;
  /** Page title as found — may be truncated or generic. */
  title: string;
  /** List price in ¥ as found (string to avoid float fiddling). */
  listCny: string | null;
  /** Promo price in ¥ if a 优惠价-style price was found. */
  promoCny: string | null;
  /** Whether the list price looks like a pre-promo (优惠前) price. */
  promoNote: "pre_promo" | "promo_found" | null;
  /** Seller SKU colors — seller truth, never translated. */
  colors: string[];
  /** Non-color SKU axes (sizes etc.) — seller truth. */
  sizeAxes: TaobaoSkuAxis[];
  /** Gallery image URLs (absolute https). */
  gallery: string[];
};

export type TaobaoBlocked = {
  ok: false;
  blocked: true;
  reason: string;
};

export type TaobaoFound = {
  ok: true;
  item: TaobaoItem;
  fetchedAt: string;
};

export type TaobaoResult = TaobaoFound | TaobaoBlocked;

/** Extract a Taobao numeric item id from a URL or pasted share text. */
export function extractItemId(raw: string): string | null {
  const url = normalizeSourceLink(raw);
  if (!url) return null;
  const direct = url.match(/[?&]id=(\d{6,})/);
  if (direct) return direct[1];
  const path = url.match(/\/i(\d{6,})\.htm/i);
  if (path) return path[1];
  return null;
}

/** Detect the classic Taobao bot-block / login-wall pages. */
export function looksBlocked(html: string): boolean {
  if (!html || html.length < 2000) return true;
  return (
    html.includes("访问受限") ||
    html.includes("访问被拒绝") ||
    html.includes("安全验证") ||
    html.includes("S11") && html.includes("tfs") ||
    /window\.location\.href\s*=\s*["']https?:\/\/(login|passport)\.taobao\.com/i.test(html)
  );
}

function decodeHtmlEntities(text: string): string {
  return text
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
}

/** Pull the first JSON-ish prop block like {"pid":"1627207","name":"颜色分类","values":[...]}. */
type SkuProp = { name: string; values: { name?: string; vid?: string }[] };

function extractSkuProps(html: string): SkuProp[] {
  const props: SkuProp[] = [];
  // skuBase props: {"pid":"...","name":"颜色分类","values":[{"vid":"...","name":"杏色",...},...]}
  const re =
    /\{[^{}]*"pid"\s*:\s*"(\d+)"[^{}]*"name"\s*:\s*"((?:[^"\\]|\\.)+)"[^{}]*"values"\s*:\s*\[((?:[^\[\]]|\[(?:[^\[\]])*\])*)\]\s*\}/g;
  let match: RegExpExecArray | null;
  while ((match = re.exec(html)) !== null) {
    const name = decodeHtmlEntities(match[2]);
    const valuesRaw = match[3];
    const values: { name?: string; vid?: string }[] = [];
    const valueRe = /\{[^{}]*"name"\s*:\s*"((?:[^"\\]|\\.)+)"[^{}]*\}/g;
    let valueMatch: RegExpExecArray | null;
    while ((valueMatch = valueRe.exec(valuesRaw)) !== null) {
      const valueName = decodeHtmlEntities(valueMatch[1]).trim();
      if (valueName) values.push({ name: valueName });
    }
    if (values.length) props.push({ name, values });
  }
  return props;
}

function extractOg(html: string, property: string): string | null {
  const re = new RegExp(
    `<meta[^>]+property=["']${property}["'][^>]+content=["']([^"']+)["']`,
    "i",
  );
  const match = html.match(re);
  if (match) return decodeHtmlEntities(match[1]);
  const re2 = new RegExp(
    `<meta[^>]+content=["']([^"']+)["'][^>]+property=["']${property}["']`,
    "i",
  );
  const match2 = html.match(re2);
  return match2 ? decodeHtmlEntities(match2[1]) : null;
}

function extractTitle(html: string): string {
  const og = extractOg(html, "og:title");
  if (og) return og;
  const match = html.match(/<title>([^<]{1,200})<\/title>/i);
  return match ? decodeHtmlEntities(match[1]).trim() : "";
}

/**
 * Find list ¥ and promo ¥. Taobao embeds several price fields; we prefer:
 *  - defaultItemPrice / priceText as the list price
 *  - a separate 优惠价/promo price when present
 */
function extractPrices(html: string): {
  listCny: string | null;
  promoCny: string | null;
  promoNote: TaobaoItem["promoNote"];
} {
  const pick = (patterns: RegExp[]): string | null => {
    for (const re of patterns) {
      const match = html.match(re);
      if (match) return match[1];
    }
    return null;
  };
  const listCny = pick([
    /"defaultItemPrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"/,
    /"priceText"\s*:\s*"(\d+(?:\.\d{1,2})?)"/,
    /"reservePrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"/,
    /"price"\s*:\s*"(\d+(?:\.\d{1,2})?)"/,
  ]);
  const promoCny = pick([
    /"promoPrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"/,
    /"promotionPrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"/,
    /"salePrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"/,
  ]);
  let promoNote: TaobaoItem["promoNote"] = null;
  if (promoCny) promoNote = "promo_found";
  else if (/优惠前|券后|预估到手/.test(html) && listCny) promoNote = "pre_promo";
  return { listCny, promoCny, promoNote };
}

function extractGallery(html: string, limit = 12): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  const push = (raw: string) => {
    let url = raw.trim();
    if (!url) return;
    if (url.startsWith("//")) url = `https:${url}`;
    if (!/^https?:\/\//i.test(url)) return;
    if (seen.has(url)) return;
    seen.add(url);
    if (out.length < limit) out.push(url);
  };
  const ogImage = extractOg(html, "og:image");
  if (ogImage) push(ogImage);
  const picsMatch = html.match(/"auctionImages"\s*:\s*\[([^\]]{1,4000})\]/);
  if (picsMatch) {
    const urlRe = /"(?:https?:)?\/\/[^"]+\.(?:jpe?g|png|webp)(?:\?[^"]*)?"/gi;
    let m: RegExpExecArray | null;
    while ((m = urlRe.exec(picsMatch[1])) !== null) push(m[0].slice(1, -1));
  }
  // generic pics array fallback
  if (out.length === 0) {
    const picsMatch2 = html.match(/"pics"\s*:\s*\[([^\]]{1,4000})\]/);
    if (picsMatch2) {
      const urlRe = /"(?:https?:)?\/\/[^"]+\.(?:jpe?g|png|webp)(?:\?[^"]*)?"/gi;
      let m: RegExpExecArray | null;
      while ((m = urlRe.exec(picsMatch2[1])) !== null) push(m[0].slice(1, -1));
    }
  }
  return out;
}

const COLOR_AXIS_RE = /颜色|色号|colour|color/i;

/** Parse already-fetched HTML into a TaobaoItem. Never invents values. */
export function parseTaobaoHtml(html: string, itemId: string): TaobaoItem {
  const skuProps = extractSkuProps(html);
  const colors: string[] = [];
  const sizeAxes: TaobaoSkuAxis[] = [];
  for (const prop of skuProps) {
    const values = prop.values.map((v) => v.name ?? "").filter(Boolean);
    if (!values.length) continue;
    if (COLOR_AXIS_RE.test(prop.name)) {
      for (const value of values) {
        if (!colors.includes(value)) colors.push(value);
      }
    } else {
      sizeAxes.push({ name: prop.name, values });
    }
  }
  const { listCny, promoCny, promoNote } = extractPrices(html);
  return {
    itemId,
    title: extractTitle(html),
    listCny,
    promoCny,
    promoNote,
    colors,
    sizeAxes,
    gallery: extractGallery(html),
  };
}

/** Server-side fetch of the listing page, following short links. */
export async function fetchTaobaoItem(rawLink: string): Promise<TaobaoResult> {
  const startUrl = normalizeSourceLink(rawLink);
  if (!startUrl) {
    return { ok: false, blocked: true, reason: "Không thấy link Taobao hợp lệ." };
  }
  const id = extractItemId(startUrl) ?? "";
  const candidates = id
    ? [
        startUrl,
        `https://item.taobao.com/item.htm?id=${id}`,
        `https://h5.m.taobao.com/awp/core/detail.htm?id=${id}`,
      ]
    : [startUrl];
  const errors: string[] = [];
  for (const url of candidates) {
    try {
      const response = await fetch(url, {
        redirect: "follow",
        signal: AbortSignal.timeout(12000),
        headers: {
          "User-Agent":
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
          Accept:
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "Accept-Language": "zh-CN,zh;q=0.9",
        },
      });
      const finalId = extractItemId(response.url) ?? id;
      if (!response.ok) {
        errors.push(`${url} -> HTTP ${response.status}`);
        continue;
      }
      const html = await response.text();
      if (looksBlocked(html)) {
        errors.push(`${url} -> blocked/login-wall`);
        continue;
      }
      return {
        ok: true,
        item: parseTaobaoHtml(html, finalId),
        fetchedAt: new Date().toISOString(),
      };
    } catch (error) {
      errors.push(`${url} -> ${error instanceof Error ? error.message : "fetch failed"}`);
    }
  }
  return {
    ok: false,
    blocked: true,
    reason: `Taobao chặn fetch tự động (thử ${candidates.length} link, đều bị chặn). Nhập tay nha — submission sẽ gắn "needs manual research".`,
  };
}

/** Type guard for TaobaoItem parsed from a client payload. */
export function isTaobaoItem(value: unknown): value is TaobaoItem {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.itemId === "string" &&
    Array.isArray(v.colors) &&
    Array.isArray(v.sizeAxes) &&
    Array.isArray(v.gallery)
  );
}
