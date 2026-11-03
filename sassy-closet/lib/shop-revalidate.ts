/** Must match the shop app. POST /api/admin/revalidate reads this header. */
export const SHOP_REVALIDATE_HEADER = "x-shop-revalidate-secret";

export function readShopRevalidateConfig():
  | { ok: true; url: string; secret: string }
  | { ok: false; error: string } {
  const secret = process.env.SHOP_REVALIDATE_SECRET?.trim() ?? "";
  const rawUrl = process.env.SHOP_REVALIDATE_URL?.trim() ?? "";
  if (!secret || !rawUrl) {
    return { ok: false, error: "Shop revalidate is not configured." };
  }
  let parsed: URL;
  try {
    parsed = new URL(rawUrl);
  } catch {
    return { ok: false, error: "SHOP_REVALIDATE_URL is not a URL." };
  }
  const local = parsed.hostname === "localhost" || parsed.hostname === "127.0.0.1";
  if (parsed.protocol !== "https:" && !(parsed.protocol === "http:" && local)) {
    return { ok: false, error: "SHOP_REVALIDATE_URL must be https." };
  }
  if (parsed.username || parsed.password || parsed.hash) {
    return { ok: false, error: "SHOP_REVALIDATE_URL must not include credentials." };
  }
  if (parsed.pathname !== "/api/admin/revalidate") {
    return { ok: false, error: "SHOP_REVALIDATE_URL must be the shop revalidate path." };
  }
  return { ok: true, url: parsed.toString(), secret };
}

export async function callShopRevalidate(
  fetchImpl: typeof fetch = fetch,
): Promise<{ ok: true } | { ok: false; error: string }> {
  const config = readShopRevalidateConfig();
  if (!config.ok) {
    return config;
  }
  let response: Response;
  try {
    response = await fetchImpl(config.url, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        [SHOP_REVALIDATE_HEADER]: config.secret,
      },
      body: "{}",
      cache: "no-store",
    });
  } catch {
    return { ok: false, error: "Shop revalidate could not be reached." };
  }
  if (!response.ok) {
    return { ok: false, error: `Shop revalidate failed (${response.status}).` };
  }
  return { ok: true };
}
