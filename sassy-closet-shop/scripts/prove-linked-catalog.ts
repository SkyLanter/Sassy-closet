import { saveProductInCatalog } from "../lib/admin-ops";
import {
  getCatalogStorageInfo,
  readLiveCatalogDocument,
  readLiveCatalogRecord,
  writeLiveCatalogDocument,
} from "../lib/catalog-store";
import type { CatalogDocument, Product } from "../lib/types";

const SHOP = process.env.SHOP_ORIGIN ?? "http://127.0.0.1:43147";
const MA = "A01";

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
    headers: { "Cache-Control": "no-cache", "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
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

function asRecord(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null) {
    fail("Expected JSON object");
  }
  return value as Record<string, unknown>;
}

async function main(): Promise<void> {
  const storage = getCatalogStorageInfo();
  if (!storage.canWrite) {
    fail("Live catalog is not writable; cannot prove admin↔shop link.");
  }

  const snapshot = await readLiveCatalogDocument();
  const record = await readLiveCatalogRecord();
  console.log(`catalog source=${record.source} write=${storage.backend} mas=${snapshot.products.length}`);

  const catalogApi = await shopJson("/api/admin/catalog");
  if (catalogApi.status !== 200) {
    fail(`GET /api/admin/catalog HTTP ${catalogApi.status}`);
  }
  const catalogBody = asRecord(catalogApi.body);
  const products = catalogBody.products;
  if (!Array.isArray(products)) {
    fail("catalog JSON missing products[]");
  }
  const mas = products.map((row) => (typeof row === "object" && row && "ma" in row ? String(row.ma) : ""));
  const allow = ["A01", "S01", "P01", "P02", "P03", "P04", "P05", "K01", "H01", "A02"];
  const hub = mas.slice(0, allow.length);
  if (hub.join(",") !== allow.join(",")) {
    fail(`catalog hub ma order ${mas.join(",")}`);
  }
  if (typeof catalogBody.catalogSha !== "string" || catalogBody.catalogSha.length < 8) {
    fail("catalog JSON missing catalogSha");
  }
  const oldSha = String(catalogBody.catalogSha);

  const hasA03 = snapshot.products.some((product) => product.ma === "A03");
  const invented = await shopJson("/api/admin/save", {
    method: "POST",
    body: JSON.stringify({ ma: "A03", titleEn: "nope" }),
  });
  if (!hasA03 && invented.status !== 400) {
    fail(`Save A03 before Add must 400 (not in catalog), got ${invented.status}`);
  }
  if (hasA03 && invented.status !== 200) {
    fail(`Save A03 after Add must 200, got ${invented.status} ${JSON.stringify(invented.body)}`);
  }

  const p05 = snapshot.products.find((product) => product.ma === "P05");
  if (p05) {
    const leak = saveProductInCatalog(snapshot.products, "P05", {
      titleEn: p05.titleEn,
      titleVn: p05.titleVn,
      descriptionEn: p05.descriptionEn,
      descriptionVn: p05.descriptionVn,
      status: "available",
      priceUsd: 23,
      colors: p05.colors,
      images: p05.images,
      fulfillment: p05.fulfillment,
      sourceLink: p05.sourceLink,
    });
    if (leak.ok) {
      fail("P05 $23 must not save");
    }
  }

  const current = snapshot.products.find((product) => product.ma === MA);
  if (!current) {
    fail("A01 missing from live catalog");
  }

  const nonce = `qa-cache-${new Date().toISOString().replace(/[-:]/g, "").slice(0, 15)}`;
  const oldTitle = current.titleEn;
  const newTitle = `${oldTitle} ${nonce}`.trim();

  try {
    const save = await shopJson("/api/admin/save", {
      method: "POST",
      body: JSON.stringify({ ma: MA, titleEn: newTitle }),
    });
    if (save.status !== 200) {
      fail(`Save A01 HTTP ${save.status} ${JSON.stringify(save.body)}`);
    }
    const receipt = asRecord(save.body);
    for (const key of ["ok", "blobWritten", "catalogSha", "revalidated"] as const) {
      if (!(key in receipt)) {
        fail(`Save receipt missing ${key}`);
      }
    }
    if (receipt.ok !== true || receipt.blobWritten !== true) {
      fail("Save did not confirm Blob write");
    }
    const paths = receipt.revalidated;
    if (!Array.isArray(paths) || (!paths.includes("/") && !paths.some((path) => String(path).startsWith("/m/")))) {
      fail("revalidated[] missing public paths");
    }
    console.log("1) Save receipt", receipt.catalogSha, paths);

    const catalog2 = await shopJson("/api/admin/catalog");
    const sha2 = String(asRecord(catalog2.body).catalogSha ?? "");
    if (!sha2 || sha2 === oldSha) {
      fail("catalogSha unchanged after Save — silent Save");
    }
    console.log(`2) catalogSha ${oldSha.slice(0, 12)} -> ${sha2.slice(0, 12)}`);

    let saw = false;
    for (let i = 1; i <= 2; i += 1) {
      const pdp = await shopGet(`/m/${MA}`);
      if (pdp.status !== 200) {
        fail(`GET /m/${MA} ${pdp.status}`);
      }
      if (pdp.text.includes(nonce)) {
        saw = true;
        console.log(`3) GET ${i} /m/${MA} has nonce`);
        break;
      }
      console.log(`3) GET ${i} /m/${MA} missing nonce (one STALE allowed)`);
    }
    if (!saw) {
      fail(`/m/${MA} still missing nonce after two warms — cache drift`);
    }

    const home = await shopGet("/");
    if (home.status !== 200 || !home.text.includes(MA)) {
      fail("Home missing A01 after Save");
    }
    if (hasA03 && !home.text.includes("A03")) {
      fail("Home missing A03 after Add");
    }
    if (home.text.includes("$23")) {
      fail("Home published $23");
    }
    if (!home.text.includes("Message to buy")) {
      fail("Home lost Message to buy look lock");
    }
    if (!home.text.includes("/products/") || !home.text.includes("cover.jpg?")) {
      fail("Home covers must be /products/{MA}/cover.jpg?v=");
    }

    const a03 = await shopGet("/m/A03");
    if (hasA03 && a03.status !== 200) {
      fail(`/m/A03 must 200 after Add, got ${a03.status}`);
    }
    if (!hasA03 && a03.status !== 404) {
      fail(`/m/A03 must 404 until Add, got ${a03.status}`);
    }

    const revalidateGet = await shopGet("/api/admin/revalidate");
    if (![200, 401, 403, 405].includes(revalidateGet.status)) {
      fail(`GET /api/admin/revalidate must exist, got ${revalidateGet.status}`);
    }
    const revalidatePost = await shopJson("/api/admin/revalidate", { method: "POST" });
    if (revalidatePost.status !== 200) {
      fail(`POST /api/admin/revalidate HTTP ${revalidatePost.status}`);
    }

    const restore = await shopJson("/api/admin/save", {
      method: "POST",
      body: JSON.stringify({ ma: MA, titleEn: oldTitle }),
    });
    if (restore.status !== 200) {
      fail(`Restore A01 HTTP ${restore.status}`);
    }
    console.log("4) A01 title restored");
  } finally {
    await writeLiveCatalogDocument(snapshot);
    const restored = await readLiveCatalogDocument();
    const restoredA01 = restored.products.find((product: Product) => product.ma === MA);
    if (!restoredA01 || restoredA01.titleEn !== snapshot.products.find((product) => product.ma === MA)?.titleEn) {
      fail("Failed to restore live catalog snapshot");
    }
  }

  void (await readLiveCatalogDocument() as CatalogDocument);
  console.log("linked catalog proof ok");
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
