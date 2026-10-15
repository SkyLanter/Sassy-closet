/**
 * Read-only mãs already on the sell catalog.
 * This module never writes the catalog, intake store, or data/held.json.
 */
import { normalizeMa, parseHubMa } from "./mint";
import { createFileShopCatalogPort, shopCatalogPortFromEnv } from "./shop-catalog-store";

type CatalogReader = {
  read(): Promise<unknown | null>;
};

export async function readLiveCatalogMas(): Promise<readonly string[]> {
  const file = process.env.SHOP_CATALOG_FILE?.trim() ?? "";
  const dataDir = process.env.SASSY_DATA_DIR?.trim() ?? "";
  if (dataDir && !file) return [];
  if (dataDir && file) return masFromPort(createFileShopCatalogPort(file));
  const selected = shopCatalogPortFromEnv();
  if (!selected.ok) return [];
  return masFromPort(selected.port);
}

async function masFromPort(port: CatalogReader): Promise<readonly string[]> {
  let document: unknown;
  try {
    document = await port.read();
  } catch {
    throw liveUnreadable();
  }
  if (document == null) throw liveUnreadable();
  return catalogProductMas(document);
}

function catalogProductMas(document: unknown): string[] {
  if (!isRecord(document) || !Array.isArray(document.products)) throw liveUnreadable();
  const mas: string[] = [];
  const seen = new Set<string>();
  for (const raw of document.products) {
    if (!isRecord(raw) || typeof raw.ma !== "string") throw liveUnreadable();
    const ma = normalizeMa(raw.ma);
    if (!parseHubMa(ma) || seen.has(ma)) throw liveUnreadable();
    seen.add(ma);
    mas.push(ma);
  }
  return mas;
}

function liveUnreadable(): Error {
  return Object.assign(new Error("Không kiểm được mã đang live."), { status: 503 });
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
