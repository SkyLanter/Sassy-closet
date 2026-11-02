/**
 * Pure checks for the read-only browser smoke.
 * GET observations only: status, robots header, HTML, and the PDP price text.
 */

export function canonicalMa(value) {
  const code = String(value ?? "").trim().toUpperCase();
  const match = code.match(/^([A-Z])(\d+)$/);
  if (!match) return code;
  return `${match[1]}${String(Number(match[2])).padStart(2, "0")}`;
}

export function visiblePriceOk(text) {
  const value = String(text ?? "").replace(/\s+/g, " ").trim();
  return value === "$25" || value === "$25.00";
}

function attr(tag, key) {
  const match = tag.match(new RegExp(`\\b${key}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s"'>]+))`, "i"));
  if (!match) return "";
  return match[1] ?? match[2] ?? match[3] ?? "";
}

export function noindexPresent(header, html) {
  if (/noindex/i.test(String(header ?? ""))) return true;
  const tags = String(html ?? "").match(/<meta\b[^>]*>/gi) ?? [];
  for (const tag of tags) {
    if (attr(tag, "name").toLowerCase() !== "robots") continue;
    if (/noindex/i.test(attr(tag, "content"))) return true;
  }
  return false;
}

function walk(data, out) {
  if (!data || typeof data !== "object") return;
  if (Array.isArray(data)) {
    for (const item of data) walk(item, out);
    return;
  }
  out.push(data);
  if (Array.isArray(data["@graph"])) walk(data["@graph"], out);
}

export function s06JsonLdPrices(html) {
  const re = /<script\b[^>]*type\s*=\s*(?:"application\/ld\+json"|'application\/ld\+json')[^>]*>([\s\S]*?)<\/script>/gi;
  const prices = [];
  let match = re.exec(String(html ?? ""));
  while (match) {
    let data;
    try {
      data = JSON.parse(match[1].trim());
    } catch {
      return { error: "json-ld parse failed", prices };
    }
    const nodes = [];
    walk(data, nodes);
    for (const node of nodes) {
      const type = node["@type"];
      const types = Array.isArray(type) ? type : [type];
      if (!types.includes("Product")) continue;
      if (canonicalMa(node.sku) !== "S06") continue;
      const offers = Array.isArray(node.offers) ? node.offers : node.offers ? [node.offers] : [];
      for (const offer of offers) {
        if (offer && offer.price != null) {
          prices.push({
            price: String(offer.price).trim(),
            currency: String(offer.priceCurrency ?? "").trim().toUpperCase(),
          });
        }
      }
    }
    match = re.exec(String(html ?? ""));
  }
  return { prices };
}

export function s06JsonLdOk(result) {
  if (!result || result.error) return false;
  if (!Array.isArray(result.prices) || result.prices.length !== 1) return false;
  const offer = result.prices[0];
  const price = Number(offer.price);
  return offer.currency === "USD" && Number.isFinite(price) && price === 25;
}

export function heldStatusOk(status) {
  return status === 404;
}

export function plan({ shops, intake, held }) {
  const checks = [];
  for (const shop of shops) {
    const origin = String(shop).replace(/\/+$/, "");
    checks.push({ kind: "noindex", url: `${origin}/` });
    checks.push({ kind: "s06", url: `${origin}/m/S06` });
    for (const ma of held) {
      checks.push({ kind: "held", url: `${origin}/m/${ma}`, ma });
    }
  }
  checks.push({ kind: "noindex", url: `${String(intake).replace(/\/+$/, "")}/` });
  return checks;
}

export function originOf(value) {
  const url = new URL(value);
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error(`unsupported scheme ${url.protocol}`);
  }
  return url.origin;
}
