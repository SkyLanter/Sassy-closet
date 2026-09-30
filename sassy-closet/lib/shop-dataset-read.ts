import { listShopCatalog } from "@/lib/shop-catalog";
import { loadShopCatalogForAdmin } from "@/lib/shop-catalog-store";
import {
  isAllowedShopOrigin,
  publicCatalogUrlFromSitemap,
  rowsFromShopCatalog,
  type ShopDatasetRow,
} from "@/lib/intake-dataset";

const CACHE_MS = 60_000;
const FETCH_MS = 2_500;

let cached: { at: number; rows: ShopDatasetRow[] } | null = null;

export function shopPublicOrigin(): string {
  const raw = process.env.SHOP_PUBLIC_ORIGIN?.trim() ?? "";
  if (raw && isAllowedShopOrigin(raw)) return new URL(raw).origin;
  return "https://sassycloset.vercel.app";
}

/** Read-only. Token catalog first, then the public shop Blob file. Never writes. */
export async function loadShopDatasetRows(): Promise<ShopDatasetRow[] | null> {
  if (cached && Date.now() - cached.at < CACHE_MS) return cached.rows;
  const fromToken = await readTokenRows();
  if (fromToken) {
    cached = { at: Date.now(), rows: fromToken };
    return fromToken;
  }
  const fromPublic = await shopDatasetFromPublicShop(fetch, shopPublicOrigin());
  if (fromPublic) {
    cached = { at: Date.now(), rows: fromPublic };
    return fromPublic;
  }
  return null;
}

export async function shopDatasetFromPublicShop(
  fetchImpl: typeof fetch,
  origin: string,
  timeoutMs = FETCH_MS,
): Promise<ShopDatasetRow[] | null> {
  if (!isAllowedShopOrigin(origin)) return null;
  const sitemap = await fetchText(fetchImpl, `${origin}/sitemap.xml`, timeoutMs);
  if (!sitemap) return null;
  const catalogUrl = publicCatalogUrlFromSitemap(sitemap);
  if (!catalogUrl) return null;
  const body = await fetchText(fetchImpl, catalogUrl, timeoutMs);
  if (!body) return null;
  try {
    return rowsFromShopCatalog(listShopCatalog(JSON.parse(body) as unknown));
  } catch {
    return null;
  }
}

async function readTokenRows(): Promise<ShopDatasetRow[] | null> {
  try {
    return rowsFromShopCatalog(await loadShopCatalogForAdmin());
  } catch {
    return null;
  }
}

async function fetchText(fetchImpl: typeof fetch, url: string, timeoutMs: number): Promise<string | null> {
  try {
    const response = await fetchImpl(url, {
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(timeoutMs),
    });
    if (!response.ok) return null;
    return await response.text();
  } catch {
    return null;
  }
}
