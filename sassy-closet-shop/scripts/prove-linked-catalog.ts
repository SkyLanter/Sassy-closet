import { saveProductInCatalog } from "../lib/admin-ops";
import { readLiveCatalogDocument } from "../lib/catalog-store";
import type { Product } from "../lib/types";

const SHOP = process.env.SHOP_ORIGIN ?? "http://127.0.0.1:43147";

function fail(message: string): never {
  throw new Error(message);
}

async function shopGet(path: string): Promise<{ status: number; text: string; headers: Headers }> {
  const response = await fetch(`${SHOP}${path}`, {
    cache: "no-store",
    headers: { "Cache-Control": "no-cache", Pragma: "no-cache" },
  });
  return { status: response.status, text: await response.text(), headers: response.headers };
}

async function shopJson(path: string, init?: RequestInit): Promise<{ status: number; body: unknown }> {
  const response = await fetch(`${SHOP}${path}`, {
    cache: "no-store",
    ...init,
    headers: { "Cache-Control": "no-cache", "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  const text = await response.text();
  let body: unknown = text;
  try {
    body = JSON.parse(text) as unknown;
  } catch {
    // keep text
  }
  return { status: response.status, body };
}

async function main(): Promise<void> {
  const admin = await shopGet("/admin");
  if (admin.status !== 404) {
    fail(`GET /admin must 404, got ${admin.status}`);
  }
  const home = await shopGet("/");
  if (home.status !== 200) {
    fail(`GET / HTTP ${home.status}`);
  }
  if (home.text.includes("Shop tools") || home.text.includes("Công cụ shop")) {
    fail("Customer home still renders Shop tools");
  }

  for (const path of ["/api/admin/catalog", "/api/admin/save", "/api/admin/add"]) {
    const closed = await shopJson(path, path.endsWith("/catalog") ? undefined : { method: "POST", body: "{}" });
    if (closed.status !== 404) {
      fail(`${path} must 404, got ${closed.status}`);
    }
  }

  const revalidateGet = await shopGet("/api/admin/revalidate");
  if (revalidateGet.status !== 405) {
    fail(`GET /api/admin/revalidate must 405, got ${revalidateGet.status}`);
  }
  const revalidatePost = await shopJson("/api/admin/revalidate", { method: "POST" });
  if (revalidatePost.status !== 401) {
    fail(`POST /api/admin/revalidate without secret must 401, got ${revalidatePost.status}`);
  }
  const secret = process.env.SHOP_REVALIDATE_SECRET?.trim() ?? "";
  if (secret) {
    const allowed = await shopJson("/api/admin/revalidate", {
      method: "POST",
      headers: { "x-shop-revalidate-secret": secret },
    });
    if (allowed.status !== 200) {
      fail(`POST /api/admin/revalidate with secret HTTP ${allowed.status}`);
    }
  }

  const snapshot = await readLiveCatalogDocument();
  const p05 = snapshot.products.find((product: Product) => product.ma === "P05");
  if (p05) {
    const leak = saveProductInCatalog(snapshot.products, "P05", {
      titleEn: p05.titleEn,
      titleVn: p05.titleVn,
      descriptionEn: p05.descriptionEn,
      descriptionVn: p05.descriptionVn,
      status: "available",
      priceUsd: 28,
      colors: p05.colors,
      images: p05.images,
      fulfillment: p05.fulfillment,
      sourceLink: p05.sourceLink,
    });
    if (!leak.ok) {
      fail(`P05 catalog USD must save, got ${leak.error}`);
    }
    if (leak.products.find((product) => product.ma === "P05")?.priceUsd !== 28) {
      fail("P05 must keep the saved catalog USD");
    }
  }
  console.log("customer admin surface ok (no catalog write)");
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
